"""RAG 索引编排：抽数据 → 切分 → embed → 入库 → 持久化 → 写 RagIndexJob。"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
from sqlalchemy.orm import Session

from app.db.database import DB_PATH
from app.models import RagIndexJob
from app.services.rag.data_sources import (
    iter_candidate_chunks,
    iter_jd_chunks,
    iter_job_skill_chunks,
    iter_skill_chunks,
)
from app.services.rag.embedder import Embedder
from app.services.rag.errors import RagError, RagInitError
from app.services.rag.models import RawChunk
from app.services.rag.vector_store import VectorStore


logger = logging.getLogger(__name__)


SOURCE_REGISTRY: dict[str, Callable[[Session], object]] = {
    "jd": iter_jd_chunks,
    "job_skill": iter_job_skill_chunks,
    "skill": iter_skill_chunks,
    "candidate": iter_candidate_chunks,
}


# 数据目录：backend/data/rag/
RAG_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "rag"
RAG_MODEL_DIR = RAG_DATA_DIR / "models"


def _index_path_for(source_type: str) -> Path:
    return RAG_DATA_DIR / f"{source_type}.index"


def _collect_chunks(iterator_factory, db: Session) -> list[RawChunk]:
    chunks: list[RawChunk] = []
    errors = 0
    for chunk in iterator_factory(db):
        try:
            if chunk and chunk.text:
                chunks.append(chunk)
        except Exception as exc:
            errors += 1
            logger.warning("跳过异常 chunk：%s", exc)
    if errors:
        logger.warning("抽数据阶段共有 %d 条 chunk 被跳过", errors)
    return chunks


def _store_meta_payload(chunk: RawChunk) -> dict:
    meta = dict(chunk.metadata or {})
    meta["source_type"] = chunk.source_type
    meta["ref_id"] = chunk.ref_id
    meta["text"] = chunk.text
    return meta


def build_index(
    source_type: str,
    db: Session,
    embedder: Embedder,
    store: VectorStore,
    *,
    force_rebuild: bool = False,
) -> RagIndexJob:
    """对单个数据源构建索引。返回 RagIndexJob 记录。"""
    if source_type not in SOURCE_REGISTRY:
        raise RagError(f"未知数据源：{source_type}")

    job = RagIndexJob(
        source_type=source_type,
        status="running",
        started_at=datetime.utcnow(),
        model_name=getattr(embedder, "model_name", ""),
        index_path=str(_index_path_for(source_type)),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        iterator = SOURCE_REGISTRY[source_type]
        chunks = _collect_chunks(iterator, db)
        if not chunks:
            logger.warning("[RAG] 数据源 %s 未抽取到任何 chunk", source_type)
            job.chunk_count = 0
            job.status = "success"
            job.completed_at = datetime.utcnow()
            db.commit()
            return job

        texts = [chunk.text for chunk in chunks]
        vectors: np.ndarray = embedder.encode(texts)
        if vectors.shape[0] != len(chunks):
            raise RagInitError(
                f"embedder 输出向量数 ({vectors.shape[0]}) 与 chunks 数 ({len(chunks)}) 不一致"
            )

        if force_rebuild and hasattr(store, "clear"):
            store.clear()
        store.add(vectors, [_store_meta_payload(chunk) for chunk in chunks])
        store.save(_index_path_for(source_type))

        job.chunk_count = len(chunks)
        job.status = "success"
        job.completed_at = datetime.utcnow()
        db.commit()
        logger.info("[RAG] 索引 %s 完成，%d 条 chunk", source_type, len(chunks))
    except Exception as exc:
        logger.exception("[RAG] 索引 %s 构建失败", source_type)
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = datetime.utcnow()
        db.commit()
        raise

    db.refresh(job)
    return job


def build_all(
    db: Session,
    embedder: Embedder,
    stores: dict[str, VectorStore],
) -> dict[str, RagIndexJob]:
    """对所有数据源构建索引。stores 需包含 SOURCE_REGISTRY 的全部 key。"""
    results: dict[str, RagIndexJob] = {}
    for source_type in SOURCE_REGISTRY:
        store = stores.get(source_type)
        if store is None:
            logger.warning("[RAG] 缺少 %s 的 store，跳过", source_type)
            continue
        try:
            results[source_type] = build_index(source_type, db, embedder, store)
        except Exception:
            logger.exception("[RAG] %s 构建失败，继续下一个", source_type)
    return results
