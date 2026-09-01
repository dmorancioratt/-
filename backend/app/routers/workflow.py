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
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import RagDocument, WorkflowConfig
from app.services.document_parser import extract_resume_text
from app.services.rag.chunker import split_text
from app.services.ai_provider import AIProviderError, analyze_with_ai
from app.services.rag.embedder import BGESmallZhEmbedder, Embedder, FakeEmbedder
from app.services.rag.errors import RagError, RagInitError
from app.services.rag.indexer import RAG_MODEL_DIR
from app.services.rag.retriever import retrieve
from app.services.rag.vector_store import (
    FaissVectorStore,
    get_user_docs_store,
    save_user_docs_store,
)


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/workflow", tags=["workflow"])


UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "data" / "rag_uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt", ".md"}
APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
_workflow_embedder: Embedder | None = None


def _get_workflow_embedder() -> Embedder:
    """Use deterministic fake vectors only in tests; production always uses BGE."""
    global _workflow_embedder
    if _workflow_embedder is None:
        _workflow_embedder = (
            FakeEmbedder(dim=512)
            if APP_ENV == "test"
            else BGESmallZhEmbedder(cache_dir=RAG_MODEL_DIR)
        )
    return _workflow_embedder


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


# ---------- 文档上传 ----------


@router.post("/docs/upload", response_model=DocumentOut)
async def upload_doc(
    file: UploadFile = File(...),
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

    # 写入 user_docs 向量库
    store = get_user_docs_store()
    embedder = _get_workflow_embedder()
    try:
        vectors = embedder.encode(chunks)
        metadatas = [
            {
                "chunk_id": i,
                "text": c,
                "source_type": "user_docs",
                "ref_id": doc.id,
                "filename": doc.filename,
            }
            for i, c in enumerate(chunks)
        ]
        start_idx = store.size()
        for i, m in enumerate(metadatas):
            m["chunk_id"] = start_idx + i
        store.add(vectors, metadatas)
        save_user_docs_store()
    except (RagError, RagInitError) as exc:
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

    user_docs = get_user_docs_store()
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

    embedder = _get_workflow_embedder()
    try:
        hits = retrieve(
            req.question,
            embedder,
            {"user_docs": user_docs},
            top_k=retrieve_top_k,
        )
    except (RagError, RagInitError) as exc:
        stages.append({"stage": "向量检索", "status": "error", "output": str(exc)})
        raise HTTPException(status_code=503, detail=f"真实向量检索不可用：{exc}") from exc

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
        stages.append({"stage": "大模型生成", "status": "warn", "output": "无检索证据，未调用 AI 生成"})
        return TestRunResponse(answer=None, evidence=[], confidence=0.0, stages_log=stages)

    try:
        ai_result = analyze_with_ai(
            "workflow_rag_answer",
            {
                "question": req.question,
                "evidence_block": "\n\n".join(
                    f"source_type={hit.source_type} ref_id={hit.ref_id}\n{hit.text}"
                    for hit in hits
                ),
                "retrieved_evidence": evidence,
            },
        )
    except AIProviderError as exc:
        stages.append({"stage": "大模型生成", "status": "error", "output": str(exc)})
        raise HTTPException(status_code=503, detail=f"真实 AI 服务不可用：{exc}") from exc

    result = ai_result.get("result") or {}
    answer = str(result.get("answer") or "").strip() or None
    cited = result.get("evidence") if isinstance(result.get("evidence"), list) else []
    confidence = max(0.0, min(1.0, float(result.get("confidence") or 0.0)))
    stages.append({"stage": "大模型生成", "status": "done", "output": f"已由 {ai_result.get('provider')} / {ai_result.get('model')} 生成"})
    stages.append({
        "stage": "引用校验",
        "status": "done" if cited else "warn",
        "output": f"模型返回 {len(cited)} 条引用" if cited else "模型未返回可校验引用",
    })

    return TestRunResponse(
        answer=answer,
        evidence=evidence,
        confidence=confidence,
        stages_log=stages,
    )
