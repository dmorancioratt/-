"""RAG 检索：多源召回 → 合并排序 → 返回 Hit 列表。"""

from __future__ import annotations

import logging
from typing import Any

from app.services.rag.embedder import Embedder
from app.services.rag.models import Hit
from app.services.rag.vector_store import VectorStore


logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    embedder: Embedder,
    stores: dict[str, VectorStore],
    *,
    top_k: int = 5,
    source_types: list[str] | None = None,
    filters: dict[str, Any] | None = None,
    per_source_top_k: int | None = None,
) -> list[Hit]:
    """对 query 做向量化召回，按 source 分别取 Top-K 后合并按 score 降序。"""
    if not query or not query.strip():
        return []
    if not stores:
        return []

    target_sources = source_types or list(stores.keys())
    per_source = per_source_top_k if per_source_top_k is not None else max(top_k, 5)

    query_vec = embedder.encode_one(query)

    candidates: list[tuple[int, float, str]] = []
    # (chunk_id, score, source_type)
    for source_type in target_sources:
        store = stores.get(source_type)
        if store is None:
            continue
        try:
            hits = store.search(query_vec, per_source, filters=filters)
        except Exception as exc:
            logger.warning("[RAG] 源 %s 检索失败：%s", source_type, exc)
            continue
        for chunk_id, score in hits:
            candidates.append((chunk_id, score, source_type))

    candidates.sort(key=lambda item: item[1], reverse=True)

    results: list[Hit] = []
    for chunk_id, score, source_type in candidates[: top_k]:
        store = stores[source_type]
        meta = store.get_metadata(chunk_id) or {}
        text = meta.get("text", "")
        meta = {k: v for k, v in meta.items() if k != "text"}
        results.append(
            Hit(
                chunk_id=chunk_id,
                text=text,
                score=score,
                source_type=source_type,
                ref_id=int(meta.get("ref_id", 0)),
                metadata=meta,
            )
        )
    return results