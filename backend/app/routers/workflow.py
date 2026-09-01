"""RAG 工作流编辑器后端接口。

- 文档上传/列表/删除/切片 → 入库到 user_docs 向量库（独立于现有 4 数据源）
- 工作流配置 CRUD（节点位置 + 节点配置）
- 工作流 dry-run：复用现有 retriever + LLM
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import RagDocument, User, WorkflowConfig
from app.services.auth import require_roles
from app.services.document_parser import extract_resume_text
from app.services.ai_provider import AIProviderError
from app.services.hallucination_guard import get_governance_rules, guard_payload
from app.services.rag.chunker import split_text
from app.services.rag.embedder import get_embedder
from app.services.rag.errors import RagError
from app.services.rag.prompts import analyze_rag, build_user_payload
from app.services.rag.retriever import retrieve
from app.services.rag.vector_store import (
    get_user_docs_store,
    save_user_docs_store,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/workflow",
    tags=["workflow"],
    dependencies=[Depends(require_roles("admin", "hr"))],
)


UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "data" / "rag_uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt", ".md"}


# ---------- Pydantic schemas ----------


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    char_count: int
    chunk_count: int
    indexed: bool
    created_at: datetime


class ChunkRequest(BaseModel):
    chunk_size: int = Field(default=500, ge=50, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class ChunkResponse(BaseModel):
    document_id: int
    chunk_count: int
    chunks_preview: list[str] = Field(default_factory=list)


class WorkflowConfigOut(BaseModel):
    id: int
    name: str
    is_default: bool
    graph_json: dict
    node_settings: dict
    created_at: datetime
    updated_at: datetime


class WorkflowConfigSave(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    is_default: bool = False
    graph_json: dict = Field(default_factory=dict)
    node_settings: dict = Field(default_factory=dict)


class TestRunRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class TestRunResponse(BaseModel):
    answer: str | None = None
    evidence: list[dict] = Field(default_factory=list)
    confidence: float = 0.0
    stages_log: list[dict] = Field(default_factory=list)


def _valid_citations(result: dict, hits: list) -> list[dict]:
    """Keep only model citations whose quote exists verbatim in retrieved text."""
    citations = result.get("evidence") if isinstance(result, dict) else []
    if not isinstance(citations, list):
        return []
    hit_texts = [str(hit.text or "") for hit in hits]
    valid: list[dict] = []
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        quote = str(citation.get("quote") or "").strip()
        if quote and any(quote in hit_text for hit_text in hit_texts):
            valid.append(citation)
    return valid


# ---------- 文档上传 ----------


@router.post("/docs/upload", response_model=DocumentOut)
async def upload_doc(
    file: UploadFile = File(...),
    user: User = Depends(require_roles("admin", "hr")),
    db: Session = Depends(get_db),
) -> DocumentOut:
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {suffix}；允许 {sorted(ALLOWED_FILE_TYPES)}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空")

    try:
        text, file_type = extract_resume_text(file.filename, content)
    except Exception as exc:
        logger.exception("[workflow] 解析文档失败")
        raise HTTPException(status_code=400, detail=f"解析失败：{exc}") from exc

    if not text:
        raise HTTPException(status_code=400, detail="文档解析后内容为空")

    storage_path = UPLOAD_ROOT / f"{int(time.time() * 1000)}_{file.filename}"
    try:
        storage_path.write_bytes(content)
    except Exception as exc:
        logger.warning("[workflow] 落盘失败：%s", exc)
        storage_path = Path()

    doc = RagDocument(
        filename=file.filename,
        file_type=file_type or suffix.lstrip("."),
        char_count=len(text),
        chunk_count=0,
        indexed=False,
        uploaded_by=user.id,
        storage_path=str(storage_path),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        char_count=doc.char_count,
        chunk_count=doc.chunk_count,
        indexed=doc.indexed,
        created_at=doc.created_at,
    )


@router.get("/docs", response_model=list[DocumentOut])
def list_docs(db: Session = Depends(get_db)) -> list[DocumentOut]:
    docs = db.scalars(select(RagDocument).order_by(RagDocument.id.desc())).all()
    return [
        DocumentOut(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            char_count=d.char_count,
            chunk_count=d.chunk_count,
            indexed=d.indexed,
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.delete("/docs/{doc_id}", response_model=dict)
def delete_doc(doc_id: int, db: Session = Depends(get_db)) -> dict:
    doc = db.get(RagDocument, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="文档不存在")
    if doc.storage_path and os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass
    # 从 user_docs 向量库移除该文档的 chunk（Faiss 不支持原地删除，用重建方式）
    try:
        embedder = get_embedder()
        store = get_user_docs_store(dim=int(embedder.dim))
        removed = store.remove_by_ref_id(doc.id, embedder)
        if removed:
            save_user_docs_store()
            logger.info("[workflow] 已从向量库移除文档 %d 的 %d 条 chunk", doc.id, removed)
    except Exception as exc:
        logger.warning("[workflow] 清理向量库失败（忽略）：%s", exc)
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}


@router.post("/docs/{doc_id}/chunk", response_model=ChunkResponse)
def chunk_doc(
    doc_id: int,
    req: ChunkRequest,
    db: Session = Depends(get_db),
) -> ChunkResponse:
    doc = db.get(RagDocument, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="文档不存在")
    if not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=400, detail="原文件已丢失，无法切片")

    with open(doc.storage_path, "rb") as f:
        content = f.read()
    text, _ = extract_resume_text(doc.filename, content)
    chunks = split_text(text, chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)

    if not chunks:
        raise HTTPException(status_code=400, detail="切片后内容为空")

    # 写入 user_docs 向量库（真实 BGE 语义向量）
    embedder = get_embedder()
    store = get_user_docs_store(dim=int(embedder.dim))
    try:
        # 先移除该文档之前入库的旧 chunk，避免重复切片导致向量重复
        store.remove_by_ref_id(doc.id, embedder)
        vectors = embedder.encode(chunks)
        metadatas = [
            {
                "text": c,
                "source_type": "user_docs",
                "ref_id": doc.id,
                "filename": doc.filename,
            }
            for c in chunks
        ]
        store.add(vectors, metadatas)
        save_user_docs_store()
    except RagError as exc:
        raise HTTPException(status_code=503, detail=f"向量化失败：{exc}") from exc

    doc.chunk_count = len(chunks)
    doc.indexed = True
    db.commit()
    db.refresh(doc)
    return ChunkResponse(
        document_id=doc.id,
        chunk_count=len(chunks),
        chunks_preview=chunks[:3],
    )


# ---------- 工作流配置 CRUD ----------


def _to_out(cfg: WorkflowConfig) -> WorkflowConfigOut:
    try:
        graph = json.loads(cfg.graph_json or "{}")
    except json.JSONDecodeError:
        graph = {}
    try:
        settings = json.loads(cfg.node_settings or "{}")
    except json.JSONDecodeError:
        settings = {}
    return WorkflowConfigOut(
        id=cfg.id,
        name=cfg.name,
        is_default=cfg.is_default,
        graph_json=graph,
        node_settings=settings,
        created_at=cfg.created_at,
        updated_at=cfg.updated_at,
    )


@router.get("/configs", response_model=list[WorkflowConfigOut])
def list_configs(db: Session = Depends(get_db)) -> list[WorkflowConfigOut]:
    rows = db.scalars(select(WorkflowConfig).order_by(WorkflowConfig.id.desc())).all()
    return [_to_out(r) for r in rows]


@router.get("/configs/{cfg_id}", response_model=WorkflowConfigOut)
def get_config(cfg_id: int, db: Session = Depends(get_db)) -> WorkflowConfigOut:
    cfg = db.get(WorkflowConfig, cfg_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return _to_out(cfg)


@router.post("/configs", response_model=WorkflowConfigOut)
def create_config(req: WorkflowConfigSave, db: Session = Depends(get_db)) -> WorkflowConfigOut:
    existing = db.scalar(select(WorkflowConfig).where(WorkflowConfig.name == req.name))
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"工作流名称已存在：{req.name}")
    cfg = WorkflowConfig(
        name=req.name,
        is_default=req.is_default,
        graph_json=json.dumps(req.graph_json, ensure_ascii=False),
        node_settings=json.dumps(req.node_settings, ensure_ascii=False),
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return _to_out(cfg)


@router.put("/configs/{cfg_id}", response_model=WorkflowConfigOut)
def update_config(cfg_id: int, req: WorkflowConfigSave, db: Session = Depends(get_db)) -> WorkflowConfigOut:
    cfg = db.get(WorkflowConfig, cfg_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="工作流不存在")
    cfg.name = req.name
    cfg.is_default = req.is_default
    cfg.graph_json = json.dumps(req.graph_json, ensure_ascii=False)
    cfg.node_settings = json.dumps(req.node_settings, ensure_ascii=False)
    db.commit()
    db.refresh(cfg)
    return _to_out(cfg)


@router.delete("/configs/{cfg_id}", response_model=dict)
def delete_config(cfg_id: int, db: Session = Depends(get_db)) -> dict:
    cfg = db.get(WorkflowConfig, cfg_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="工作流不存在")
    db.delete(cfg)
    db.commit()
    return {"deleted": cfg_id}


# ---------- Dry-run ----------


@router.post("/configs/{cfg_id}/test", response_model=TestRunResponse)
def dry_run(cfg_id: int, req: TestRunRequest, db: Session = Depends(get_db)) -> TestRunResponse:
    cfg = db.get(WorkflowConfig, cfg_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="工作流不存在")

    stages: list[dict] = []
    try:
        settings = json.loads(cfg.node_settings or "{}")
    except json.JSONDecodeError:
        settings = {}
    retrieve_top_k = int(settings.get("retrieve", {}).get("top_k", req.top_k))

    stages.append({"stage": "问题解析", "status": "done", "output": req.question[:80]})

    embedder = get_embedder()
    user_docs = get_user_docs_store(dim=int(embedder.dim))
    if user_docs.size() == 0:
        stages.append({
            "stage": "本地知识库",
            "status": "warn",
            "output": "本地知识库为空，请先上传并切分文档",
        })
    else:
        stages.append({
            "stage": "本地知识库",
            "status": "done",
            "output": f"已索引 {user_docs.size()} 个 chunks",
        })

    stages.append({
        "stage": "Top-K 检索",
        "status": "done",
        "output": f"top_k={retrieve_top_k}",
    })

    # 真实 BGE 语义检索
    try:
        hits = retrieve(
            req.question,
            embedder,
            {"user_docs": user_docs},
            top_k=retrieve_top_k,
        )
    except RagError as exc:
        stages.append({"stage": "向量检索", "status": "error", "output": str(exc)})
        return TestRunResponse(answer=None, evidence=[], confidence=0.0, stages_log=stages)

    evidence = [
        {
            "chunk_id": h.chunk_id,
            "text": h.text[:200],
            "score": round(h.score, 4),
            "source_type": h.source_type,
            "ref_id": h.ref_id,
        }
        for h in hits
    ]
    stages.append({
        "stage": "向量检索",
        "status": "done",
        "output": f"返回 {len(hits)} 条证据，最高相似度 {hits[0].score:.3f}" if hits else "无匹配",
    })

    if not hits:
        stages.append({"stage": "大模型生成", "status": "warn", "output": "无检索证据，未调用大模型"})
        stages.append({"stage": "幻觉检测", "status": "warn", "output": "无答案可检测"})
        stages.append({"stage": "引用校验", "status": "warn", "output": "无可用引用"})
        return TestRunResponse(answer=None, evidence=[], confidence=0.0, stages_log=stages)

    # 只基于真实检索证据调用已配置的大模型，不生成本地拼接的伪答案。
    answer: str | None = None
    confidence = 0.0
    try:
        payload = build_user_payload(req.question, hits)
        payload["_rag_hits"] = hits
        ai_result = analyze_rag("rag_query_knowledge_base", payload)
        inner = (ai_result.get("result") or {}) if isinstance(ai_result, dict) else {}
        answer = inner.get("answer") or inner.get("summary") or None
        confidence = float(inner.get("confidence") or 0.0)
        stages.append({"stage": "大模型生成", "status": "done", "output": "已基于证据生成回答"})
    except AIProviderError as exc:
        logger.warning("[workflow] 大模型生成失败：%s", exc)
        raise HTTPException(status_code=502, detail=f"大模型生成失败：{exc}") from exc
    valid_citations = _valid_citations(inner, hits)
    rules = get_governance_rules(db)
    guard_ok, guard_issues = guard_payload(
        {"confidence": confidence, "evidence": valid_citations},
        rules,
    )
    stages.append({
        "stage": "幻觉检测",
        "status": "done" if guard_ok else "warn",
        "output": "置信度与证据链校验通过" if guard_ok else "；".join(guard_issues),
    })
    stages.append({
        "stage": "引用校验",
        "status": "done" if valid_citations else "warn",
        "output": f"{len(valid_citations)} 条引用通过原文逐字校验",
    })

    return TestRunResponse(
        answer=answer,
        evidence=evidence,
        confidence=confidence,
        stages_log=stages,
    )


# ---------------------------------------------------------------------------
# 流式 dry-run（SSE）：逐阶段推送真实进度，供前端底部进度条/步骤条联动
# ---------------------------------------------------------------------------

_STREAM_STAGES = ["问题解析", "本地知识库", "Top-K 检索", "向量检索", "大模型生成", "幻觉检测", "引用校验"]


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/configs/{cfg_id}/test-stream")
def dry_run_stream(
    cfg_id: int,
    req: TestRunRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    cfg = db.get(WorkflowConfig, cfg_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="工作流不存在")
    try:
        settings = json.loads(cfg.node_settings or "{}")
    except json.JSONDecodeError:
        settings = {}
    retrieve_top_k = int(settings.get("retrieve", {}).get("top_k", req.top_k))
    total = len(_STREAM_STAGES)

    def _stage_event(idx: int, status: str, output: str) -> dict:
        finished = status in ("done", "warn", "error")
        return {
            "event": "stage",
            "index": idx,
            "total": total,
            "stage": _STREAM_STAGES[idx],
            "status": status,
            "output": output,
            "progress": round((idx + (1 if finished else 0.5)) / total * 100),
        }

    def gen():
        stages_log: list[dict] = []

        def emit(idx, status, output):
            ev = _stage_event(idx, status, output)
            if status in ("done", "warn", "error"):
                stages_log.append({"stage": ev["stage"], "status": ev["status"], "output": ev["output"]})
            return _sse(ev)

        # 1 问题解析
        yield emit(0, "running", "解析用户问题")
        yield emit(0, "done", req.question[:80])

        # 2 本地知识库
        yield emit(1, "running", "加载本地知识库")
        embedder = get_embedder()
        user_docs = get_user_docs_store(dim=int(embedder.dim))
        if user_docs.size() == 0:
            yield emit(1, "warn", "本地知识库为空，请先上传并切分文档")
        else:
            yield emit(1, "done", f"已索引 {user_docs.size()} 个 chunks")

        # 3 Top-K 检索参数
        yield emit(2, "running", "确定检索参数")
        yield emit(2, "done", f"top_k={retrieve_top_k}")

        # 4 向量检索（真耗时：BGE 编码 + faiss 召回）
        yield emit(3, "running", "语义向量召回中")
        try:
            hits = retrieve(req.question, embedder, {"user_docs": user_docs}, top_k=retrieve_top_k)
        except RagError as exc:
            yield emit(3, "error", str(exc))
            yield _sse({"event": "result", "answer": None, "evidence": [], "confidence": 0.0, "stages_log": stages_log})
            return
        evidence = [
            {
                "chunk_id": h.chunk_id,
                "text": h.text[:200],
                "score": round(h.score, 4),
                "source_type": h.source_type,
                "ref_id": h.ref_id,
            }
            for h in hits
        ]
        yield emit(3, "done", f"返回 {len(hits)} 条证据，最高相似度 {hits[0].score:.3f}" if hits else "无匹配")

        if not hits:
            yield emit(4, "warn", "无检索证据，未调用大模型")
            yield emit(5, "warn", "无答案可检测")
            yield emit(6, "warn", "无可用引用")
            yield _sse({"event": "result", "answer": None, "evidence": [], "confidence": 0.0, "stages_log": stages_log})
            return

        # 5 大模型生成（真耗时：LLM 调用）
        yield emit(4, "running", "调用大模型生成答案")
        answer: str | None = None
        confidence = 0.0
        try:
            payload = build_user_payload(req.question, hits)
            payload["_rag_hits"] = hits
            ai_result = analyze_rag("rag_query_knowledge_base", payload)
            inner = (ai_result.get("result") or {}) if isinstance(ai_result, dict) else {}
            answer = inner.get("answer") or inner.get("summary") or None
            confidence = float(inner.get("confidence") or 0.0)
            yield emit(4, "done", "已基于证据生成回答")
        except AIProviderError as exc:
            logger.warning("[workflow] 大模型生成失败：%s", exc)
            yield emit(4, "error", f"大模型生成失败：{exc}")
            yield emit(5, "warn", "无答案可检测")
            yield emit(6, "warn", "无答案可校验引用")
            yield _sse({"event": "result", "answer": None, "evidence": evidence, "confidence": 0.0, "stages_log": stages_log})
            return

        valid_citations = _valid_citations(inner, hits)
        rules = get_governance_rules(db)
        guard_ok, guard_issues = guard_payload(
            {"confidence": confidence, "evidence": valid_citations},
            rules,
        )

        # 6 幻觉检测
        yield emit(5, "running", "校验事实一致性")
        yield emit(
            5,
            "done" if guard_ok else "warn",
            "置信度与证据链校验通过" if guard_ok else "；".join(guard_issues),
        )

        # 7 引用校验
        yield emit(6, "running", "核对引用来源")
        yield emit(
            6,
            "done" if valid_citations else "warn",
            f"{len(valid_citations)} 条引用通过原文逐字校验",
        )

        yield _sse({"event": "result", "answer": answer, "evidence": evidence, "confidence": confidence, "stages_log": stages_log})

    return StreamingResponse(gen(), media_type="text/event-stream")
