"""向量存储抽象层 + Faiss 实现。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np

from app.services.rag.errors import RagInitError


logger = logging.getLogger(__name__)


@runtime_checkable
class VectorStore(Protocol):
    def add(self, vectors: np.ndarray, metadatas: list[dict]) -> None: ...
    def search(
        self,
        query_vec: np.ndarray,
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[int, float]]: ...
    def save(self, path: Path) -> None: ...
    def load(self, path: Path) -> bool: ...
    def size(self) -> int: ...


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """行级 L2 归一化，便于用内积模拟余弦。"""
    if vectors.size == 0:
        return vectors
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return (vectors / norms).astype(np.float32)


class FaissVectorStore:
    """基于 faiss.IndexFlatIP 的精确检索。"""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._index = None
        self._metadatas: list[dict] = []

    def _ensure_index(self) -> Any:
        if self._index is None:
            try:
                import faiss
            except ImportError as exc:
                raise RagInitError("faiss-cpu 未安装，请先 pip install faiss-cpu") from exc
            self._index = faiss.IndexFlatIP(self.dim)
        return self._index

    def add(self, vectors: np.ndarray, metadatas: list[dict]) -> None:
        if vectors.size == 0:
            return
        if len(metadatas) != vectors.shape[0]:
            raise ValueError("vectors 与 metadatas 数量必须一致")
        index = self._ensure_index()
        normalized = _normalize(vectors)
        index.add(normalized)
        # 用当前 store 大小作为起始 chunk_id
        start = len(self._metadatas)
        for offset, meta in enumerate(metadatas):
            new_meta = dict(meta)
            new_meta.setdefault("chunk_id", start + offset)
            new_meta.setdefault("source_type", new_meta.get("source_type", "unknown"))
            new_meta.setdefault("ref_id", new_meta.get("ref_id", 0))
            new_meta.setdefault("text", new_meta.get("text", ""))
            self._metadatas.append(new_meta)

    def search(
        self,
        query_vec: np.ndarray,
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[int, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        k = min(top_k, self._index.ntotal)
        normalized = _normalize(query_vec.reshape(1, -1).astype(np.float32))
        scores, ids = self._index.search(normalized, k)
        results: list[tuple[int, float]] = []
        for chunk_id, score in zip(ids[0].tolist(), scores[0].tolist()):
            if chunk_id < 0:
                continue
            if filters and not self._match_filters(chunk_id, filters):
                continue
            results.append((chunk_id, float(score)))
        return results

    def _match_filters(self, chunk_id: int, filters: dict[str, Any]) -> bool:
        meta = self._metadatas[chunk_id] if 0 <= chunk_id < len(self._metadatas) else {}
        for key, expected in filters.items():
            actual = meta.get(key)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            else:
                if str(actual) != str(expected):
                    return False
        return True

    def save(self, path: Path) -> None:
        index = self._ensure_index()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        index_path = path.with_suffix(".index")
        meta_path = path.with_suffix(".meta.json")
        try:
            import faiss

            faiss.write_index(index, str(index_path))
        except ImportError as exc:
            raise RagInitError("faiss-cpu 未安装，无法持久化") from exc
        meta_path.write_text(
            json.dumps(self._metadatas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, path: Path) -> bool:
        path = Path(path)
        index_path = path.with_suffix(".index")
        meta_path = path.with_suffix(".meta.json")
        if not (index_path.exists() and meta_path.exists()):
            return False
        try:
            import faiss
        except ImportError as exc:
            raise RagInitError("faiss-cpu 未安装，无法加载") from exc
        self._index = faiss.read_index(str(index_path))
        self._metadatas = json.loads(meta_path.read_text(encoding="utf-8"))
        return True

    def size(self) -> int:
        return 0 if self._index is None else int(self._index.ntotal)

    def get_metadata(self, chunk_id: int) -> dict | None:
        if 0 <= chunk_id < len(self._metadatas):
            return self._metadatas[chunk_id]
        return None


# ---------- UserDocsStore 单例 ----------
# 用于 workflow 编辑器中用户上传到本地知识库的文档向量。
# 与现有 SOURCE_REGISTRY 4 个数据源完全隔离，不污染 rag_index_jobs 表。
_USER_DOCS_DIM = 512
_user_docs_store: "FaissVectorStore | None" = None


def get_user_docs_store() -> "FaissVectorStore":
    global _user_docs_store
    if _user_docs_store is None:
        from app.services.rag.indexer import RAG_DATA_DIR
        store = FaissVectorStore(dim=_USER_DOCS_DIM)
        _path = RAG_DATA_DIR / "user_docs.index"
        store.load(_path)
        _user_docs_store = store
    return _user_docs_store


def save_user_docs_store() -> None:
    if _user_docs_store is not None:
        from app.services.rag.indexer import RAG_DATA_DIR
        _user_docs_store.save(RAG_DATA_DIR / "user_docs.index")


class InMemoryVectorStore:
    """测试用 fallback：纯 numpy 实现，无 faiss 依赖。"""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self._vectors: np.ndarray = np.zeros((0, dim), dtype=np.float32)
        self._metadatas: list[dict] = []

    def add(self, vectors: np.ndarray, metadatas: list[dict]) -> None:
        if vectors.size == 0:
            return
        if len(metadatas) != vectors.shape[0]:
            raise ValueError("vectors 与 metadatas 数量必须一致")
        normalized = _normalize(vectors)
        self._vectors = np.vstack([self._vectors, normalized])
        start = len(self._metadatas)
        for offset, meta in enumerate(metadatas):
            new_meta = dict(meta)
            new_meta.setdefault("chunk_id", start + offset)
            self._metadatas.append(new_meta)

    def search(
        self,
        query_vec: np.ndarray,
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[int, float]]:
        if self._vectors.shape[0] == 0:
            return []
        k = min(top_k, self._vectors.shape[0])
        normalized = _normalize(query_vec.reshape(1, -1).astype(np.float32))
        scores = (self._vectors @ normalized.T).flatten()
        order = np.argsort(-scores)
        results: list[tuple[int, float]] = []
        for idx in order:
            chunk_id = int(idx)
            if filters and not self._match_filters(chunk_id, filters):
                continue
            results.append((chunk_id, float(scores[chunk_id])))
            if len(results) >= k:
                break
        return results

    def _match_filters(self, chunk_id: int, filters: dict[str, Any]) -> bool:
        meta = self._metadatas[chunk_id] if 0 <= chunk_id < len(self._metadatas) else {}
        for key, expected in filters.items():
            actual = meta.get(key)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            else:
                if str(actual) != str(expected):
                    return False
        return True

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta_path = path.with_suffix(".meta.json")
        np.save(path.with_suffix(".npy"), self._vectors)
        meta_path.write_text(
            json.dumps(self._metadatas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self, path: Path) -> bool:
        path = Path(path)
        npy_path = path.with_suffix(".npy")
        meta_path = path.with_suffix(".meta.json")
        if not (npy_path.exists() and meta_path.exists()):
            return False
        self._vectors = np.load(npy_path)
        self._metadatas = json.loads(meta_path.read_text(encoding="utf-8"))
        return True

    def size(self) -> int:
        return int(self._vectors.shape[0])

    def get_metadata(self, chunk_id: int) -> dict | None:
        if 0 <= chunk_id < len(self._metadatas):
            return self._metadatas[chunk_id]
        return None