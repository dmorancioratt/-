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

        cache_folder = str(self._cache_dir) if self._cache_dir else None
        local = self._find_local_snapshot()

        # 1) 优先直接用本地缓存的模型目录加载（零网络请求）
        if local is not None:
            try:
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
                self._model = SentenceTransformer(str(local))
                return
            except Exception:
                os.environ.pop("HF_HUB_OFFLINE", None)
                os.environ.pop("TRANSFORMERS_OFFLINE", None)

        # 2) 回退：按 model_name 加载（缓存缺失时触发下载）
        try:
            self._model = SentenceTransformer(self.model_name, cache_folder=cache_folder)
        except Exception as exc:
            raise RagInitError(f"BGE 模型加载失败：{exc}") from exc

    def _find_local_snapshot(self) -> Path | None:
        if not self._cache_dir or not self._cache_dir.exists():
            return None
        for snap in self._cache_dir.glob("models--*/snapshots/*"):
            if snap.is_dir() and ((snap / "model.safetensors").exists() or (snap / "pytorch_model.bin").exists()):
                return snap
        return None

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


# ---------------------------------------------------------------------------
# 共享 embedder 单例
# ---------------------------------------------------------------------------

# 与 indexer.RAG_MODEL_DIR 保持同一目录；embedder 不能 import indexer（避免循环依赖）
_DEFAULT_MODEL_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "rag" / "models"

_shared_embedder: "Embedder | None" = None


def get_embedder(cache_dir: Path | None = None, *, force_fake: bool | None = None) -> Embedder:
    """模块级懒加载单例：优先 BGE-small-zh-v1.5，加载失败回退 FakeEmbedder。

    rag 主线与 workflow 本地知识库线共用同一实例，保证向量维度（512）与语义一致。
    可通过环境变量 RAG_EMBEDDER=fake 强制使用伪向量（测试/无网环境）。
    """
    global _shared_embedder
    if _shared_embedder is None:
        if force_fake is None:
            env = os.getenv("RAG_EMBEDDER", "").strip().lower()
            force_fake = env in {"fake", "mock", "0"}
        if force_fake:
            logger.info("[RAG] 强制使用 FakeEmbedder（RAG_EMBEDDER=fake）")
            _shared_embedder = FakeEmbedder(dim=512)
        else:
            try:
                candidate = BGESmallZhEmbedder(cache_dir=cache_dir or _DEFAULT_MODEL_CACHE_DIR)
                # 触发真实加载（首次会下载模型）；失败则回退 fake，确保 fallback 真正生效
                candidate.encode(["embedder 预热检测"])
                _shared_embedder = candidate
            except RagInitError as exc:
                logger.warning("[RAG] BGE 加载失败（%s），回退到 FakeEmbedder", exc)
                _shared_embedder = FakeEmbedder(dim=512)
    return _shared_embedder