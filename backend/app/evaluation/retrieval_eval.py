"""RAG 检索质量离线评测。

用真实 embedder 对「技能 chunk」做语义检索，量化指标：
- hit1 / hit5：相关技能是否出现在 Top-1 / Top-5（命中率）
- recall5：相关技能在 Top-5 中被召回的比例
- mrr：首个相关技能排名的倒数均值（衡量"相关结果排得靠不靠前"）

评测集 QUERY_SET 里 query 使用口语化近义表达，relevant 为技能图谱中真实存在的技能名，
避免精确匹配作弊、真正测语义召回能力。返回 dict，由 run_eval 组装成 EvalResult。
"""

from __future__ import annotations

import numpy as np

from app.db.database import SessionLocal
from app.services.rag.data_sources import iter_skill_chunks
from app.services.rag.embedder import get_embedder

# 口语 query -> 应召回的相关技能名（均来自现有技能图谱）
QUERY_SET: list[dict] = [
    {"query": "会写 Python 后端服务", "relevant": ["Python", "FastAPI", "Flask"]},
    {"query": "前端页面和数据可视化开发", "relevant": ["Vue", "React"]},
    {"query": "大模型应用与检索增强", "relevant": ["RAG", "LangChain", "Prompt Engineering"]},
    {"query": "向量检索和语义搜索", "relevant": ["向量数据库", "RAG"]},
    {"query": "数据分析与统计报表", "relevant": ["SQL", "数据质量", "数据治理"]},
    {"query": "容器化和云原生部署", "relevant": ["Docker", "Kubernetes", "Spring Cloud"]},
    {"query": "分布式大数据计算", "relevant": ["Hadoop", "Spark", "Flink", "Kafka"]},
    {"query": "机器学习和深度学习模型训练", "relevant": ["机器学习", "深度学习"]},
    {"query": "Java 后端系统开发", "relevant": ["Java", "Spring Boot"]},
    {"query": "缓存和消息队列", "relevant": ["Redis", "Kafka"]},
    {"query": "知识图谱与实体关系建模", "relevant": ["知识图谱"]},
]


def _load_skill_chunks() -> list[dict]:
    """抽取技能 chunk，返回 [{text, skill_name}, ...]。"""
    chunks: list[dict] = []
    with SessionLocal() as db:
        for chunk in iter_skill_chunks(db):
            name = (chunk.metadata or {}).get("skill_name", "")
            if name:
                chunks.append({"text": chunk.text, "skill_name": name})
    return chunks


def run(top_k: int = 5) -> dict:
    chunks = _load_skill_chunks()
    if not chunks:
        return {
            "task": "rag_retrieval",
            "task_label": "RAG 检索质量",
            "samples": 0,
            "metrics": {"hit1": 0.0, "hit5": 0.0, "recall5": 0.0, "mrr": 0.0},
            "error_cases": [],
            "notes": "技能图谱为空，无法评测",
        }

    embedder = get_embedder()
    vectors = embedder.encode([c["text"] for c in chunks])  # (N, dim)
    queries = [item["query"] for item in QUERY_SET]
    qvecs = embedder.encode(queries)  # (M, dim)

    scores = qvecs @ vectors.T  # (M, N) 归一化后内积 = 余弦相似度

    name_to_idx: dict[str, list[int]] = {}
    for i, c in enumerate(chunks):
        name_to_idx.setdefault(c["skill_name"], []).append(i)

    hit1 = hit5 = 0
    reciprocal_ranks: list[float] = []
    recalled_total = 0
    relevant_total = 0
    error_cases: list[dict] = []
    total = len(QUERY_SET)

    for q_idx, item in enumerate(QUERY_SET):
        relevant_idxs: set[int] = set()
        for name in item["relevant"]:
            relevant_idxs.update(name_to_idx.get(name, []))
        relevant_total += max(1, len(item["relevant"]))

        order = np.argsort(-scores[q_idx])[:top_k]
        top_idx = set(int(i) for i in order)

        hit = relevant_idxs & top_idx
        if hit:
            hit5 += 1
            if int(order[0]) in relevant_idxs:
                hit1 += 1
        else:
            error_cases.append({"query": item["query"], "relevant": item["relevant"]})

        recalled_total += len(relevant_idxs & top_idx)

        rank = next((r + 1 for r, idx in enumerate(order) if int(idx) in relevant_idxs), 0)
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)

    return {
        "task": "rag_retrieval",
        "task_label": "RAG 检索质量",
        "samples": total,
        "metrics": {
            "hit1": round(hit1 / total, 4),
            "hit5": round(hit5 / total, 4),
            "recall5": round(recalled_total / relevant_total, 4),
            "mrr": round(float(np.mean(reciprocal_ranks)), 4),
        },
        "error_cases": error_cases[:10],
        "notes": f"基于 {len(chunks)} 条技能 chunk，真实 embedder 语义检索，Top-{top_k}",
    }