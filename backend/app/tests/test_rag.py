"""RAG 模块测试。

- 单测：chunker / vector_store / retriever / prompts
- 集成：FakeEmbedder + InMemoryVectorStore 全链路

运行：
    cd backend && pytest app/tests/test_rag.py -q
"""

from __future__ import annotations

import os
from datetime import datetime

# 强制 mock 模式，AI 调用走保底模板
os.environ.setdefault("AI_PROVIDER", "mock")

import numpy as np
import pytest

from app.db.database import SessionLocal, engine, Base
from app.models import CandidateProfile, JobEntity, JobSkillRelation, RawJD, Resume, ResumeSkill, SkillEntity, User
from app.services.ai_provider import analyze_with_ai
from app.services.rag.chunker import chunk_candidate, chunk_jd, chunk_job_skill, chunk_skill
from app.services.rag.embedder import FakeEmbedder
from app.services.rag.errors import RagInitError
from app.services.rag.indexer import build_index
from app.services.rag.models import Hit, RawChunk
from app.services.rag.prompts import (
    RAG_TASK_TYPES,
    build_hits_block,
    build_user_payload,
    install_mock_patch,
    rag_mock_result,
    register_rag_tasks,
)
from app.services.rag.retriever import retrieve
from app.services.rag.vector_store import FaissVectorStore, InMemoryVectorStore


@pytest.fixture(autouse=True)
def _ensure_tables():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def fake_embedder():
    return FakeEmbedder(dim=64)


# ---------------------------------------------------------------------------
# chunker 测试
# ---------------------------------------------------------------------------


def test_chunk_jd_builds_one_chunk():
    raw = RawJD(id=1, title="Python 后端工程师", content="招聘熟悉 FastAPI、PostgreSQL、Docker 的工程师。", text_hash="x", parse_status="raw")
    chunks = chunk_jd(raw)
    assert len(chunks) == 1
    assert chunks[0].source_type == "jd"
    assert chunks[0].ref_id == 1
    assert "FastAPI" in chunks[0].text
    assert chunks[0].metadata["title"] == "Python 后端工程师"


def test_chunk_jd_skips_empty():
    chunks = chunk_jd(RawJD(id=2, title="", content="", text_hash="y", parse_status="raw"))
    assert chunks == []


def test_chunk_skill_basic():
    skill = SkillEntity(id=10, name="RAG", category="AI", description="检索增强生成")
    chunks = chunk_skill(skill)
    assert len(chunks) == 1
    assert chunks[0].source_type == "skill"
    assert "RAG" in chunks[0].text
    assert "检索增强生成" in chunks[0].text


def test_chunk_job_skill_combines_fields():
    job = JobEntity(id=1, name="AI 工程师", domain="AI", level="中级", description="做 AI 应用")
    skill = SkillEntity(id=2, name="Python", category="编程", description="编程语言")
    rel = JobSkillRelation(id=5, job_id=1, skill_id=2, relation_type="requires", weight=0.9)
    chunks = chunk_job_skill(job, rel, skill)
    assert len(chunks) == 1
    assert "AI 工程师" in chunks[0].text
    assert "Python" in chunks[0].text
    assert chunks[0].metadata["relation_type"] == "requires"


def test_chunk_candidate_builds_multi_fields(db):
    import uuid

    username = f"rag_test_user_{uuid.uuid4().hex[:8]}"
    user = User(username=username, role="candidate", display_name="测试候选")
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = CandidateProfile(
        user_id=user.id,
        skills='["Python", "RAG"]',
        certificates='["AWS"]',
        projects='["知识库问答系统"]',
        internships='[]',
        awards='[]',
        completeness=0.5,
    )
    db.add(profile)
    resume = Resume(
        user_id=user.id,
        name="测试候选",
        education="本科",
        major="计算机",
        school="示例大学",
        intention="AI 工程师",
        projects="[]",
        internships="[]",
        certificates="[]",
        competitions="[]",
        raw_text="第一段：熟悉 Python 与 RAG。\n\n第二段：做过企业知识库项目。\n\n第三段补全 " + "很长的文字 " * 100,
        source_filename="rag_test.txt",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    db.add(ResumeSkill(resume_id=resume.id, skill_name="Python", level="高级", evidence="负责后端开发"))
    db.commit()

    rs_skills = [ResumeSkill(resume_id=resume.id, skill_name="Python", level="高级", evidence="负责后端开发")]
    chunks = chunk_candidate(profile, resume, rs_skills)
    fields = {chunk.metadata.get("field") for chunk in chunks}
    assert {"skills", "certificates", "projects", "resume_skills", "resume_paragraph"} <= fields


# ---------------------------------------------------------------------------
# vector_store 测试
# ---------------------------------------------------------------------------


def test_inmemory_store_add_search():
    store = InMemoryVectorStore(dim=16)
    rng = np.random.default_rng(42)
    vectors = rng.standard_normal((5, 16)).astype(np.float32)
    metas = [{"chunk_id": i, "source_type": "test", "ref_id": i, "text": f"text-{i}"} for i in range(5)]
    store.add(vectors, metas)
    assert store.size() == 5

    query = vectors[2] + 0.01 * rng.standard_normal(16)
    hits = store.search(query, top_k=3)
    assert len(hits) > 0
    best_id, best_score = hits[0]
    assert best_id == 2  # 加噪后仍应最接近自身


def test_inmemory_store_filters():
    store = InMemoryVectorStore(dim=8)
    vectors = np.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
        ],
        dtype=np.float32,
    )
    metas = [
        {"chunk_id": 0, "source_type": "jd", "ref_id": 1, "text": "a", "domain": "AI"},
        {"chunk_id": 1, "source_type": "jd", "ref_id": 2, "text": "b", "domain": "数据"},
        {"chunk_id": 2, "source_type": "skill", "ref_id": 3, "text": "c", "domain": "AI"},
    ]
    store.add(vectors, metas)
    hits = store.search(np.array([1, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32), top_k=5, filters={"source_type": ["jd"]})
    assert all(store.get_metadata(cid)["source_type"] == "jd" for cid, _ in hits)


def test_faiss_store_save_load(tmp_path):
    store = FaissVectorStore(dim=32)
    rng = np.random.default_rng(7)
    vectors = rng.standard_normal((6, 32)).astype(np.float32)
    metas = [{"chunk_id": i, "source_type": "jd", "ref_id": i, "text": f"jd-{i}"} for i in range(6)]
    store.add(vectors, metas)
    path = tmp_path / "jd.index"
    store.save(path)
    assert path.with_suffix(".index").exists()
    assert path.with_suffix(".meta.json").exists()

    new_store = FaissVectorStore(dim=32)
    loaded = new_store.load(path)
    assert loaded is True
    assert new_store.size() == 6
    hits = new_store.search(vectors[0], top_k=1)
    assert hits[0][0] == 0


def test_faiss_store_missing_index_returns_false(tmp_path):
    store = FaissVectorStore(dim=8)
    assert store.load(tmp_path / "missing.index") is False


# ---------------------------------------------------------------------------
# embedder 测试
# ---------------------------------------------------------------------------


def test_fake_embedder_deterministic():
    emb = FakeEmbedder(dim=32)
    v1 = emb.encode_one("hello")
    v2 = emb.encode_one("hello")
    np.testing.assert_allclose(v1, v2)
    assert v1.shape == (32,)
    assert abs(float(np.linalg.norm(v1)) - 1.0) < 0.05


# ---------------------------------------------------------------------------
# retriever 测试
# ---------------------------------------------------------------------------


def test_retriever_returns_top_k_sorted(fake_embedder):
    """FakeEmbedder 的伪向量不一定语义相关，但排序与 filter 应正确工作。"""
    store_a = InMemoryVectorStore(dim=64)
    store_b = InMemoryVectorStore(dim=64)
    store_a.add(
        fake_embedder.encode(["Python 后端开发", "Java Spring 全栈", "数据分析师 SQL"]),
        [
            {"chunk_id": 0, "source_type": "skill", "ref_id": 1, "text": "Python 后端开发", "skill_name": "Python"},
            {"chunk_id": 1, "source_type": "skill", "ref_id": 2, "text": "Java Spring 全栈", "skill_name": "Java"},
            {"chunk_id": 2, "source_type": "skill", "ref_id": 3, "text": "数据分析师 SQL", "skill_name": "SQL"},
        ],
    )
    store_b.add(
        fake_embedder.encode(["RAG 检索增强", "深度学习模型", "前端 React"]),
        [
            {"chunk_id": 0, "source_type": "jd", "ref_id": 11, "text": "RAG 检索增强", "job_name": "AI 工程师"},
            {"chunk_id": 1, "source_type": "jd", "ref_id": 12, "text": "深度学习模型", "job_name": "算法工程师"},
            {"chunk_id": 2, "source_type": "jd", "ref_id": 13, "text": "前端 React", "job_name": "前端工程师"},
        ],
    )
    stores = {"skill": store_a, "jd": store_b}
    hits = retrieve("RAG", fake_embedder, stores, top_k=4)
    assert len(hits) > 0
    assert all(isinstance(h, Hit) for h in hits)
    # 排序正确（按 score 降序）
    assert hits == sorted(hits, key=lambda x: x.score, reverse=True)
    # self-recall 验证：encode("RAG 检索增强") 自身应能召回为 Top-1
    direct_hits = retrieve("RAG 检索增强", fake_embedder, stores, top_k=3)
    assert direct_hits[0].text == "RAG 检索增强"


def test_retriever_source_types_filter(fake_embedder):
    store = InMemoryVectorStore(dim=64)
    store.add(
        fake_embedder.encode(["a", "b"]),
        [
            {"chunk_id": 0, "source_type": "jd", "ref_id": 1, "text": "a"},
            {"chunk_id": 1, "source_type": "skill", "ref_id": 2, "text": "b"},
        ],
    )
    stores = {"jd": store, "skill": store}
    hits = retrieve("anything", fake_embedder, stores, top_k=5, source_types=["skill"])
    assert all(h.source_type == "skill" for h in hits)


def test_retriever_empty_query(fake_embedder):
    store = InMemoryVectorStore(dim=64)
    store.add(
        fake_embedder.encode(["a"]),
        [{"chunk_id": 0, "source_type": "jd", "ref_id": 1, "text": "a"}],
    )
    assert retrieve("", fake_embedder, {"jd": store}, top_k=3) == []


# ---------------------------------------------------------------------------
# prompts 测试
# ---------------------------------------------------------------------------


def test_register_rag_tasks_idempotent():
    register_rag_tasks()
    register_rag_tasks()
    import app.services.ai_provider as ai_module
    assert "rag_query_job" in ai_module.SUPPORTED_TASKS
    assert "rag_query_skill" in ai_module.SUPPORTED_TASKS


def test_build_hits_block_includes_metadata():
    hits = [
        Hit(chunk_id=0, text="Python 后端开发", score=0.9, source_type="skill", ref_id=1, metadata={"skill_name": "Python"}),
        Hit(chunk_id=1, text="AI 工程师", score=0.7, source_type="jd", ref_id=2, metadata={"job_name": "AI 工程师"}),
    ]
    block = build_hits_block(hits)
    assert "[1]" in block
    assert "[2]" in block
    assert "skill_name=Python" in block


def test_build_user_payload_merges_extra():
    payload = build_user_payload("什么是 RAG？", hits=[], extra={"focus_skill": "RAG"})
    assert payload["question"] == "什么是 RAG？"
    assert payload["focus_skill"] == "RAG"


def test_rag_mock_result_minimal():
    res = rag_mock_result("rag_query_job", hits=[], payload={"question": "x"})
    assert res["confidence"] == 0.0
    assert len(res["evidence"]) >= 1


def test_install_mock_patch_routes_rag_calls():
    install_mock_patch()
    register_rag_tasks()
    hits = [Hit(chunk_id=0, text="RAG 示例", score=0.8, source_type="skill", ref_id=1, metadata={})]
    payload = build_user_payload("?", hits=hits)
    payload["_rag_hits"] = hits
    payload["focus_skill"] = "RAG"
    res = analyze_with_ai("rag_query_interview_hint", payload)
    assert res["provider"] == "mock"
    assert res["task_type"] == "rag_query_interview_hint"
    assert "hints" in res["result"]


# ---------------------------------------------------------------------------
# 集成测试（端到端）
# ---------------------------------------------------------------------------


def test_end_to_end_with_seed_data(db, fake_embedder):
    """使用真实 seed 数据 + FakeEmbedder + InMemoryVectorStore 跑通 index → query。"""
    from app.services.rag.data_sources import (
        iter_jd_chunks,
        iter_skill_chunks,
        iter_job_skill_chunks,
        iter_candidate_chunks,
    )

    sources = {
        "jd": (iter_jd_chunks, list(iter_jd_chunks(db))),
        "job_skill": (iter_job_skill_chunks, list(iter_job_skill_chunks(db))),
        "skill": (iter_skill_chunks, list(iter_skill_chunks(db))),
        "candidate": (iter_candidate_chunks, list(iter_candidate_chunks(db))),
    }
    stores: dict[str, InMemoryVectorStore] = {}
    for name, (_, chunks) in sources.items():
        if not chunks:
            stores[name] = InMemoryVectorStore(dim=64)
            continue
        vectors = fake_embedder.encode([c.text for c in chunks])
        store = InMemoryVectorStore(dim=64)
        metas = [
            {"chunk_id": i, "source_type": c.source_type, "ref_id": c.ref_id, "text": c.text, **c.metadata}
            for i, c in enumerate(chunks)
        ]
        store.add(vectors, metas)
        stores[name] = store

    # 跳过 db RagIndexJob 写入，直接验证 retriever
    hits = retrieve("Python", fake_embedder, stores, top_k=5)
    assert len(hits) > 0


def test_build_index_writes_rag_index_job(db, fake_embedder):
    """build_index 必须正确写 RagIndexJob 记录（status=success, chunk_count>0）。"""
    store = InMemoryVectorStore(dim=64)
    job = build_index("skill", db, fake_embedder, store)
    assert job.id is not None
    assert job.source_type == "skill"
    assert job.status == "success"
    assert job.chunk_count > 0
    assert job.completed_at is not None


def test_build_index_unknown_source_raises(db, fake_embedder):
    store = InMemoryVectorStore(dim=64)
    with pytest.raises(Exception):
        build_index("nonexistent", db, fake_embedder, store)