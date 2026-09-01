"""防幻觉效果量化评测（规则/关键词匹配，零外部依赖，可离线复现）。

思路：把「忠实度」定义为"答案与证据的 char n-gram 重叠率"——
- 忠实答案几乎逐字来自 evidence，重叠率高；
- 编造（幻觉）答案里混入了 evidence 中不存在的实体/事实，重叠率骤降。

用固定阈值对评测集做分类，与人工标注对比，产出：
- accuracy：幻觉检测准确率
- faithful_avg / hallucinated_avg：两类答案的平均忠实度（差距越大，规则区分力越强）

返回 dict，由 run_eval 组装成 EvalResult。
"""

from __future__ import annotations

import re

THRESHOLD = 0.55

CASES: list[dict] = [
    {
        "answer": "数融智联的核心产品是岗位能力图谱构建与分析系统，采用 RAG 检索增强生成技术。",
        "evidence": "数融智联的核心产品是岗位能力图谱构建与分析系统，采用 RAG 检索增强生成技术，结合岗位 JD 与候选人简历输出人岗匹配建议。",
        "label": "faithful",
    },
    {
        "answer": "岗位能力图谱系统会检索用户上传的文档并基于证据生成回答，避免编造事实。",
        "evidence": "岗位能力图谱系统采用 RAG 技术，检索用户上传的文档片段，并基于证据生成带引用的回答，避免幻觉。",
        "label": "faithful",
    },
    {
        "answer": "机器学习工程师需要掌握算法、模型训练和数据分析能力。",
        "evidence": "机器学习工程师需要掌握算法、模型训练能力。",
        "label": "faithful",
    },
    {
        "answer": "数据分析师需要熟练使用 SQL 进行统计报表和指标分析。",
        "evidence": "数据分析师需要熟练使用 SQL 进行统计报表和指标分析，并输出数据洞察。",
        "label": "faithful",
    },
    {
        "answer": "Java 开发工程师必须通过 Kubernetes 认证，并用 Docker 进行服务部署和线上运维。",
        "evidence": "Java 开发工程师需要使用 Spring Boot 进行服务开发。",
        "label": "hallucinated",
    },
    {
        "answer": "数融智联成立于 2015 年，总部在北京中关村，拥有 500 名员工，还获得了 C 轮融资。",
        "evidence": "数融智联的核心产品是岗位能力图谱构建与分析系统。",
        "label": "hallucinated",
    },
    {
        "answer": "本系统要求候选人必须通过 AWS 认证，并掌握 Kubernetes 和 Hadoop 大数据技术。",
        "evidence": "本岗位要求候选人掌握 Python 和 SQL。",
        "label": "hallucinated",
    },
    {
        "answer": "该岗位月薪 5 万元，提供股权激励，工作地点在上海张江。",
        "evidence": "该岗位负责知识图谱建模与大数据分析。",
        "label": "hallucinated",
    },
]


def _char_ngrams(text: str, n: int = 2) -> set:
    cleaned = re.sub(r"[\s，。、；：""''（）()《》【】,.!?]", "", text)
    return {cleaned[i : i + n] for i in range(len(cleaned) - n + 1)}


def faithfulness(answer: str, evidence: str) -> float:
    ans = _char_ngrams(answer)
    if not ans:
        return 1.0
    evi = _char_ngrams(evidence)
    return round(len(ans & evi) / len(ans), 4)


def run() -> dict:
    if not CASES:
        return {
            "task": "hallucination",
            "task_label": "防幻觉效果",
            "samples": 0,
            "metrics": {"accuracy": 0.0, "faithful_avg": 0.0, "hallucinated_avg": 0.0},
            "error_cases": [],
            "notes": "评测集为空",
        }

    correct = 0
    faithful_scores: list[float] = []
    hallucinated_scores: list[float] = []
    error_cases: list[dict] = []

    for case in CASES:
        score = faithfulness(case["answer"], case["evidence"])
        predicted = "faithful" if score >= THRESHOLD else "hallucinated"
        if predicted == case["label"]:
            correct += 1
        else:
            error_cases.append(
                {
                    "answer": case["answer"][:60],
                    "label": case["label"],
                    "predicted": predicted,
                    "faithfulness": score,
                }
            )
        if case["label"] == "faithful":
            faithful_scores.append(score)
        else:
            hallucinated_scores.append(score)

    total = len(CASES)
    return {
        "task": "hallucination",
        "task_label": "防幻觉效果",
        "samples": total,
        "metrics": {
            "accuracy": round(correct / total, 4),
            "faithful_avg": round(sum(faithful_scores) / len(faithful_scores), 4),
            "hallucinated_avg": round(sum(hallucinated_scores) / len(hallucinated_scores), 4),
        },
        "error_cases": error_cases[:10],
        "notes": f"char 2-gram 忠实度阈值 {THRESHOLD}，规则匹配量化",
    }