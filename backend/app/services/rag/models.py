"""RAG 模块的内部数据结构。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RawChunk:
    """从数据源抽取的、待入库的原始文本块。"""

    source_type: str
    ref_id: int
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Hit:
    """检索召回的单条命中结果。"""

    chunk_id: int
    text: str
    score: float
    source_type: str
    ref_id: int
    metadata: dict = field(default_factory=dict)