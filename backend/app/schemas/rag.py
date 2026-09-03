"""RAG 模块 Pydantic schemas（API 入参/出参）。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    source: str | None = Field(default=None, description="不传则重建全部 4 个数据源")
    force_rebuild: bool = Field(default=False, description="强制重建（默认跳过已成功的）")


class IndexStats(BaseModel):
    source_type: str
    status: str
    chunk_count: int
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str = ""


class RagHit(BaseModel):
    chunk_id: int
    text: str
    score: float
    source_type: str
    ref_id: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    source_types: list[str] | None = Field(default=None)
    filters: dict[str, Any] | None = Field(default=None)


class RagQueryResponse(BaseModel):
    answer: str | None = None
    evidence: list[RagHit] = Field(default_factory=list)
    confidence: float = 0.0
    provider: str = ""
    model: str = ""
    task_type: str = ""
    raw: dict[str, Any] | None = None


class MatchExplainRequest(BaseModel):
    candidate_id: int
    job_id: int
    question: str = Field(default="请解释这位候选人与该岗位的匹配差距及原因")
    top_k: int = Field(default=5, ge=1, le=20)


class InterviewHintRequest(BaseModel):
    candidate_id: int
    job_id: int
    focus_skill: str = Field(description="候选人声称掌握、面试官想深挖的技能")
    top_k: int = Field(default=5, ge=1, le=20)