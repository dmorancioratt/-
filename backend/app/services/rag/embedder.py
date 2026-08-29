"""Embedding 抽象层与 BGE 中文模型实现。"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np

from app.services.rag.errors import RagInitError


logger = logging.getLogger(__name__)


@runtime_checkable
class Embedder(Protocol):
    dim: int
    model_name: str

    def encode(self, texts: list[str]) -> np.ndarray: ...
    def encode_one(self, text: str) -> np.ndarray: ...


_DEFAULT_MODEL = "BAAI/bge-small-zh-v1.5"
_DEFAULT_DIM = 512


class BGESmallZhEmbedder:
    """懒加载 BGE-small-zh-v1.5；首次 encode 才下载 + 加载。"""

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        cache_dir: Path | None = None,
        batch_size: int = 32,
    ) -> None:
        self.model_name = model_name
        self.dim = _DEFAULT_DIM
        self.batch_size = batch_size
        self._cache_dir = Path(cache_dir) if cache_dir else None
        self._model = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RagInitError(
                "sentence-transformers 未安装，请先 pip install sentence-transformers"
            ) from exc

        if self._cache_dir is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(self._cache_dir))

        try:
            self._model = SentenceTransformer(self.model_name, cache_folder=str(self._cache_dir) if self._cache_dir else None)
        except Exception as exc:
            raise RagInitError(f"BGE 模型加载失败：{exc}") from exc

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        self._ensure_loaded()
        vectors = self._model.encode(  # type: ignore[union-attr]
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vectors.astype(np.float32)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]


class FakeEmbedder:
    """测试用 fake：返回固定维度 + 基于文本 hash 的伪向量，便于快速验证流程。"""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim
        self.model_name = "fake-embedder"

    def encode(self, texts: list[str]) -> np.ndarray:
        import hashlib

        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        rng = np.random.default_rng(0)
        vectors = []
        for text in texts:
            digest = hashlib.md5(text.encode("utf-8")).digest()
            seed = int.from_bytes(digest[:4], "big")
            local_rng = np.random.default_rng(seed)
            vec = local_rng.standard_normal(self.dim).astype(np.float32)
            vec /= np.linalg.norm(vec) + 1e-9
            vectors.append(vec)
        return np.stack(vectors, axis=0)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]