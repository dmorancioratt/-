"""Workflow 编辑器接口测试。"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

os.environ.setdefault("AI_PROVIDER", "mock")

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.db.init_db import seed_database  # noqa: E402
from app.main import app  # noqa: E402
from app.models import RagDocument, WorkflowConfig  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _setup_db():
    seed_database()
    yield


@pytest.fixture
def client():
    test_client = TestClient(app)
    login = test_client.post("/api/auth/login", json={"username": "admin_demo", "password": "Demo@123"})
    assert login.status_code == 200
    test_client.headers.update({"Authorization": f"Bearer {login.json()['token']}"})
    return test_client


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _cleanup(db):
    db.execute(delete(WorkflowConfig))
    db.execute(delete(RagDocument))
    db.commit()
    yield
    db.execute(delete(WorkflowConfig))
    db.execute(delete(RagDocument))
    db.commit()


def test_upload_document(client):
    """上传 txt → RagDocument 行落库 + char_count > 0。"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("这是一个测试文档，用于 RAG 工作流编辑器单元测试。\n" * 5)
        path = f.name

    with open(path, "rb") as f:
        resp = client.post(
            "/api/workflow/docs/upload",
            files={"file": ("test.txt", f, "text/plain")},
        )
    Path(path).unlink(missing_ok=True)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["filename"] == "test.txt"
    assert data["char_count"] > 0
    assert data["chunk_count"] == 0
    assert data["indexed"] is False
    with SessionLocal() as db:
        assert db.get(RagDocument, data["id"]).uploaded_by is not None


def test_workflow_requires_management_role():
    unauthenticated = TestClient(app)
    assert unauthenticated.get("/api/workflow/docs").status_code == 401
    login = unauthenticated.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    assert unauthenticated.get("/api/workflow/docs", headers=headers).status_code == 403


def test_list_and_delete_documents(client):
    """列出文档 + 删除后 404。"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("测试用文档内容。" * 20)
        path = f.name

    with open(path, "rb") as f:
        up = client.post(
            "/api/workflow/docs/upload",
            files={"file": ("a.txt", f, "text/plain")},
        )
    Path(path).unlink(missing_ok=True)
    doc_id = up.json()["id"]

    lst = client.get("/api/workflow/docs").json()
    assert any(d["id"] == doc_id for d in lst)

    deleted = client.delete(f"/api/workflow/docs/{doc_id}")
    assert deleted.status_code == 200
    miss = client.delete(f"/api/workflow/docs/{doc_id}")
    assert miss.status_code == 404


def test_chunk_document_indexes(client):
    """上传 → 切片 → 索引成功 + chunk_count > 0。"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("段落一：介绍 RAG 工作流编辑器。\n\n段落二：支持 12 类节点拖拽连线。\n\n段落三：右侧抽屉配置参数。\n" * 3)
        path = f.name
    with open(path, "rb") as f:
        up = client.post(
            "/api/workflow/docs/upload",
            files={"file": ("chunk.txt", f, "text/plain")},
        )
    Path(path).unlink(missing_ok=True)
    doc_id = up.json()["id"]

    resp = client.post(
        f"/api/workflow/docs/{doc_id}/chunk",
        json={"chunk_size": 100, "chunk_overlap": 20},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["chunk_count"] > 0
    assert len(data["chunks_preview"]) <= 3


def test_save_and_load_config(client):
    """保存 → 加载 → graph_json 一致。"""
    payload = {
        "name": "默认 RAG 流程",
        "is_default": True,
        "graph_json": {"nodes": [{"id": "input"}], "edges": []},
        "node_settings": {"retrieve": {"top_k": 5}},
    }
    create = client.post("/api/workflow/configs", json=payload)
    assert create.status_code == 200, create.text
    cfg_id = create.json()["id"]

    got = client.get(f"/api/workflow/configs/{cfg_id}").json()
    assert got["name"] == "默认 RAG 流程"
    assert got["graph_json"]["nodes"][0]["id"] == "input"
    assert got["node_settings"]["retrieve"]["top_k"] == 5

    # update
    update = client.put(
        f"/api/workflow/configs/{cfg_id}",
        json={**payload, "node_settings": {"retrieve": {"top_k": 8}}},
    )
    assert update.status_code == 200
    assert update.json()["node_settings"]["retrieve"]["top_k"] == 8

    # duplicate name → 409
    dup = client.post("/api/workflow/configs", json=payload)
    assert dup.status_code == 409


def test_dry_run_stages(client):
    """test 端点返回 stages_log，且每条 stage 有 stage/status/output。"""
    # 先确保有 chunk 数据
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("RAG 工作流编辑器测试。\n" * 4)
        path = f.name
    with open(path, "rb") as f:
        up = client.post(
            "/api/workflow/docs/upload",
            files={"file": ("dry.txt", f, "text/plain")},
        )
    Path(path).unlink(missing_ok=True)
    doc_id = up.json()["id"]
    client.post(f"/api/workflow/docs/{doc_id}/chunk", json={"chunk_size": 100, "chunk_overlap": 20})

    cfg = client.post("/api/workflow/configs", json={
        "name": "测试 dry-run",
        "graph_json": {},
        "node_settings": {"retrieve": {"top_k": 3}},
    }).json()
    cfg_id = cfg["id"]

    resp = client.post(
        f"/api/workflow/configs/{cfg_id}/test",
        json={"question": "什么是 RAG？", "top_k": 3},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "stages_log" in data
    stages = [s["stage"] for s in data["stages_log"]]
    assert "问题解析" in stages
    assert "向量检索" in stages
    assert "大模型生成" in stages
    assert all("status" in s and "output" in s for s in data["stages_log"])


def test_upload_rejects_disallowed_type(client):
    """不支持的文件类型返回 400。"""
    with tempfile.NamedTemporaryFile("w", suffix=".exe", delete=False) as f:
        f.write("fake")
        path = f.name
    with open(path, "rb") as f:
        resp = client.post(
            "/api/workflow/docs/upload",
            files={"file": ("bad.exe", f, "application/octet-stream")},
        )
    Path(path).unlink(missing_ok=True)
    assert resp.status_code == 400
