"""RAG 路由：8 个端点，覆盖索引管理与 4 类问答。

设计要点：
- Embedder / VectorStores / Retriever 都是模块级单例，首次调用懒加载。
- 索引文件不存在时，/index 端点会重新构建；/query 端点若命中失败会返回 503。
- RAG 不强制鉴权，遵循 /api/graph/* 风格。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import RagIndexJob
from app.schemas.rag import (
    IndexRequest,
    IndexStats,
    InterviewHintRequest,
    MatchExplainRequest,
    RagHit,
    RagQueryRequest,
    RagQueryResponse,
)
from app.services.ai_provider import AIProviderError
from app.services.rag.embedder import Embedder, FakeEmbedder, get_embedder
from app.services.rag.errors import RagError, RagInitError
from app.services.rag.indexer import (
    RAG_DATA_DIR,
    RAG_MODEL_DIR,
    SOURCE_REGISTRY,
    _index_path_for,
    build_all,
    build_index,
)
from app.services.rag.models import Hit
from app.services.rag.prompts import (
    analyze_rag,
    build_user_payload,
    register_rag_tasks,
)
from app.services.rag.retriever import retrieve
from app.services.rag.vector_store import FaissVectorStore, VectorStore, get_user_docs_store


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/rag", tags=["rag"])


# ---------------------------------------------------------------------------
# 模块级单例
# ---------------------------------------------------------------------------

_stores: dict[str, VectorStore] | None = None


def _get_embedder() -> Embedder:
    try:
        return get_embedder()
    except RagInitError as exc:
        raise HTTPException(status_code=503, detail=f"RAG 真实嵌入模型不可用：{exc}") from exc


def _get_stores() -> dict[str, VectorStore]:
    global _stores
    if _stores is None:
        embedder = _get_embedder()
        _stores = {source: FaissVectorStore(dim=embedder.dim) for source in SOURCE_REGISTRY}
    return _stores


def _ensure_indexes_loaded() -> dict[str, VectorStore]:
    stores = _get_stores()
    for source_type, store in stores.items():
        path = _index_path_for(source_type)
        if store.size() == 0:
            loaded = store.load(path)
            if not loaded:
                logger.info("[RAG] 索引文件缺失 %s，待 /index 调用时构建", path)
    return stores


# 启动时立即注册 RAG task 定义
register_rag_tasks()


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _hit_to_dict(hit: Hit) -> RagHit:
    return RagHit(
        chunk_id=hit.chunk_id,
        text=hit.text,
        score=hit.score,
        source_type=hit.source_type,
        ref_id=hit.ref_id,
        metadata=hit.metadata,
    )


def _to_query_response(
    hits: list[Hit],
    ai_result: dict[str, Any],
    task_type: str,
) -> RagQueryResponse:
    inner = ai_result.get("result") or {}
    answer = (
        inner.get("answer")
        or inner.get("summary")
        or inner.get("note")
        or ""
    )
    confidence = float(inner.get("confidence") or 0.0)
    return RagQueryResponse(
        answer=answer or None,
        evidence=[_hit_to_dict(h) for h in hits],
        confidence=confidence,
        provider=str(ai_result.get("provider") or ""),
        model=str(ai_result.get("model") or ""),
        task_type=task_type,
        raw=inner,
    )


def _stats_for(db: Session) -> list[IndexStats]:
    rows = db.execute(
        select(RagIndexJob).order_by(desc(RagIndexJob.id)).limit(len(SOURCE_REGISTRY) * 4)
    ).scalars().all()
    seen: dict[str, RagIndexJob] = {}
    for row in rows:
        if row.source_type not in seen:
            seen[row.source_type] = row
    out: list[IndexStats] = []
    for source in SOURCE_REGISTRY:
        job = seen.get(source)
        if job is None:
            out.append(
                IndexStats(
                    source_type=source,
                    status="never",
                    chunk_count=0,
                    started_at=__import__("datetime").datetime.utcnow(),
                    completed_at=None,
                    error_message="尚未构建",
                )
            )
        else:
            out.append(
                IndexStats(
                    source_type=job.source_type,
                    status=job.status,
                    chunk_count=job.chunk_count,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    error_message=job.error_message or "",
                )
            )
    return out


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("/index", response_model=list[IndexStats])
def index_all(req: IndexRequest, db: Session = Depends(get_db)) -> list[IndexStats]:
    """重建全部 4 个数据源索引。"""
    embedder = _get_embedder()
    stores = _get_stores()
    build_all(db, embedder, stores)
    return _stats_for(db)


@router.post("/index/{source}", response_model=IndexStats)
def index_one(source: str, req: IndexRequest, db: Session = Depends(get_db)) -> IndexStats:
    if source not in SOURCE_REGISTRY:
        raise HTTPException(status_code=400, detail=f"未知数据源：{source}")
    embedder = _get_embedder()
    stores = _get_stores()
    build_index(source, db, embedder, stores[source], force_rebuild=req.force_rebuild)
    return next(stat for stat in _stats_for(db) if stat.source_type == source)


@router.get("/stats", response_model=list[IndexStats])
def stats(db: Session = Depends(get_db)) -> list[IndexStats]:
    return _stats_for(db)


@router.get("/status")
def status(db: Session = Depends(get_db)) -> dict:
    """RAG 引擎综合状态：嵌入模型信息 + 各数据源索引状态。"""
    embedder = _get_embedder()
    return {
        "embedder": {
            "model_name": getattr(embedder, "model_name", ""),
            "dim": int(getattr(embedder, "dim", 0) or 0),
            "is_fake": isinstance(embedder, FakeEmbedder),
        },
        "sources": [stat.model_dump(mode="json") for stat in _stats_for(db)],
    }


def _do_query(
    req: RagQueryRequest,
    task_type: str,
    extra: dict[str, Any] | None,
    db: Session,
) -> RagQueryResponse:
    embedder = _get_embedder()
    stores = _ensure_indexes_loaded()
    if not stores:
        raise HTTPException(status_code=503, detail="RAG 索引未初始化")
    # 融入本地知识库（用户上传文档）作为额外检索源
    try:
        user_docs = get_user_docs_store(dim=int(embedder.dim))
    except Exception as exc:
        logger.warning("[RAG] 加载本地知识库失败：%s", exc)
        user_docs = None
    if user_docs is not None and user_docs.size() > 0:
        stores = dict(stores)
        stores["user_docs"] = user_docs

    missing = [s for s in SOURCE_REGISTRY if stores.get(s) and stores[s].size() == 0]
    if missing:
        for source in missing:
            try:
                build_index(source, db, embedder, stores[source])
            except Exception as exc:
                logger.warning("[RAG] 自动构建 %s 失败：%s", source, exc)

    hits = retrieve(
        req.question,
        embedder,
        stores,
        top_k=req.top_k,
        source_types=req.source_types,
        filters=req.filters,
    )
    payload = build_user_payload(req.question, hits, extra=extra)
    payload["_rag_hits"] = hits
    try:
        ai_result = analyze_rag(task_type, payload)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return _to_query_response(hits, ai_result, task_type)


@router.post("/query", response_model=RagQueryResponse)
def query_generic(req: RagQueryRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    return _do_query(req, task_type="rag_query_job", extra=None, db=db)


@router.post("/query/job", response_model=RagQueryResponse)
def query_job(req: RagQueryRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    return _do_query(req, task_type="rag_query_job", extra=None, db=db)


@router.post("/query/skill", response_model=RagQueryResponse)
def query_skill(req: RagQueryRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    return _do_query(req, task_type="rag_query_skill", extra=None, db=db)


@router.post("/query/match-explain", response_model=RagQueryResponse)
def query_match_explain(req: MatchExplainRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    from app.services.matching import score_match

    extra = {
        "candidate_id": req.candidate_id,
        "job_id": req.job_id,
    }
    try:
        match_report = score_match(db, candidate_id=req.candidate_id, job_id=req.job_id)
        missing = list(match_report.get("missing_skills") or [])
        matched = list(match_report.get("matched_required_skills") or [])
        extra.update(
            {
                "missing_skills": missing,
                "matched_skills": matched,
                "total_score": match_report.get("total_score"),
                "verdict_hint": match_report.get("confidence_label"),
            }
        )
        sub_req = RagQueryRequest(
            question=req.question,
            top_k=req.top_k,
            source_types=["jd", "job_skill"],
            filters=None,
        )
        return _do_query(sub_req, task_type="rag_query_match_explain", extra=extra, db=db)
    except Exception as exc:
        logger.warning("[RAG] match-explain 调用 matching 失败：%s", exc)
        sub_req = RagQueryRequest(
            question=req.question,
            top_k=req.top_k,
            source_types=["jd", "job_skill"],
            filters=None,
        )
        return _do_query(sub_req, task_type="rag_query_match_explain", extra=extra, db=db)


@router.post("/query/interview-hint", response_model=RagQueryResponse)
def query_interview_hint(req: InterviewHintRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    extra = {
        "candidate_id": req.candidate_id,
        "job_id": req.job_id,
        "focus_skill": req.focus_skill,
    }
    sub_req = RagQueryRequest(
        question=(
            f"请基于岗位对「{req.focus_skill}」的要求，深挖候选人对 {req.focus_skill} 的掌握程度。"
        ),
        top_k=req.top_k,
        source_types=["jd", "job_skill", "skill"],
        filters=None,
    )
    return _do_query(sub_req, task_type="rag_query_interview_hint", extra=extra, db=db)
