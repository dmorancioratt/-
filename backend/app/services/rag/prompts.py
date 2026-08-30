"""RAG 模块的 prompt 模板与 task 注册。

不直接修改 ai_provider.py，而是通过 register_rag_tasks() 把 4 个 RAG 场景
以 task_type 形式注入到 ai_provider.TASK_DEFINITIONS / SUPPORTED_TASKS。
routers/rag.py 在启动时调用 register_rag_tasks()。
"""

from __future__ import annotations

from typing import Any

from app.services.ai_provider import (
    TASK_DEFINITIONS,
    AIProviderError,
)

from app.services.rag.models import Hit


# ---------------------------------------------------------------------------
# 通用规则与角色
# ---------------------------------------------------------------------------

_RAG_BASE_RULES = [
    "输出必须是一个有效 JSON 对象，不要包含任何解释性外层或 markdown。",
    "所有判断必须严格基于 evidence 引用的检索片段，禁止编造原文中没有的事实。",
    "evidence 数组至少包含 1 条来源；每条 evidence.source 注明检索片段的 source_type 与 ref_id，evidence.quote 直接引用检索片段原文（50-200 字内）。",
    "confidence 必须是 0 到 1 的小数；若检索片段不足以回答问题，confidence 应低于 0.5 且 evidence 仍需给出最相关的尝试引用。",
    "面向用户的文本使用简体中文，技术名词可保留英文。",
]


# ---------------------------------------------------------------------------
# 4 个场景的 prompt 定义
# ---------------------------------------------------------------------------

JOB_DEFINITION: dict[str, Any] = {
    "instruction": (
        "扮演资深岗位分析师。基于检索片段回答用户关于「某个岗位」的提问，"
        "覆盖岗位定位、必备技能、加分技能、工具、职责、场景、证书和经验等。"
        "若用户问的是模糊概念，尝试定位到最相关的具体岗位并解释。"
    ),
    "example": {
        "summary": "对该岗位的整体回答",
        "job_name": "岗位名称（如能从 evidence 推断）",
        "required_skills": ["必备技能"],
        "preferred_skills": ["加分技能"],
        "tools": ["工具或平台"],
        "responsibilities": ["职责"],
        "scenarios": ["业务场景"],
        "answer": "面向用户的完整回答（3-6 句话）",
        "confidence": 0.85,
        "evidence": [
            {"source": "JD 原文 id=123", "quote": "原文证据片段"},
        ],
    },
}

SKILL_DEFINITION: dict[str, Any] = {
    "instruction": (
        "扮演技能词典作者。基于检索片段回答用户关于「某个技能」的定义、应用场景、"
        "关联技能、常见误区和学习路径建议。若用户未指明技能，先识别最可能想问的技能再回答。"
    ),
    "example": {
        "summary": "对该技能的整体回答",
        "skill_name": "技能名称",
        "definition": "一句话定义",
        "use_cases": ["典型应用场景"],
        "related_skills": ["关联技能"],
        "learning_tips": ["学习建议"],
        "answer": "面向用户的完整回答（3-6 句话）",
        "confidence": 0.85,
        "evidence": [
            {"source": "技能图谱 id=42", "quote": "技能描述原文片段"},
        ],
    },
}

MATCH_EXPLAIN_DEFINITION: dict[str, Any] = {
    "instruction": (
        "扮演人岗匹配顾问。基于「候选人已有技能/经历」与「岗位要求」之间的差距，"
        "结合检索片段中的真实 JD 证据，解释为什么不匹配、差在哪里、如何补齐。"
        "重点引用 evidence 中的 JD 原文片段作为依据，不要凭空补充。"
    ),
    "example": {
        "summary": "差距总览",
        "missing_skills": ["缺失技能列表"],
        "dimension_insights": [
            {
                "dimension": "维度（必备技能/加分技能/工具/项目经验 等）",
                "finding": "差距描述",
                "evidence": ["JD 原文证据"],
                "action": "建议行动",
            }
        ],
        "suggestions": ["具体提升建议"],
        "interview_focus": ["面试准备重点"],
        "answer": "面向用户的完整解释（4-8 句话）",
        "confidence": 0.8,
        "evidence": [
            {"source": "JD 原文 id=15", "quote": "原文片段"},
        ],
    },
}

INTERVIEW_HINT_DEFINITION: dict[str, Any] = {
    "instruction": (
        "扮演资深面试官。基于候选人声称掌握的 focus_skill 与该岗位的真实要求之间的差距，"
        "为数字人面试官生成 3-5 个深挖追问点，每个追问都要引用 evidence 中的岗位/JD 原文。"
        "追问要由浅入深：先让候选人解释基础概念，再追问项目落地细节，最后试探边界和取舍。"
    ),
    "example": {
        "summary": "对 focus_skill 的整体探查策略",
        "focus_skill": "深挖的技能",
        "hints": [
            {
                "level": "基础/项目/边界",
                "question": "建议追问的问题",
                "intent": "这道题在考察什么",
                "evidence_quote": "JD 原文片段作为追问依据",
            }
        ],
        "answer": "面向数字人面试官的完整策略说明（4-6 句话）",
        "confidence": 0.8,
        "evidence": [
            {"source": "JD 原文 id=12", "quote": "原文片段"},
        ],
    },
}


KNOWLEDGE_BASE_DEFINITION: dict[str, Any] = {
    "instruction": (
        "扮演企业本地知识库问答助手。严格基于 evidence 中的检索片段回答用户关于本地知识库文档的问题。"
        "只引用 evidence 中出现的片段内容，禁止编造文档里没有的事实。"
        "若检索片段不足以回答，明确说明信息不足并把 confidence 降到 0.5 以下，evidence 仍给出最相关的尝试引用。"
    ),
    "example": {
        "summary": "基于检索片段的整体回答",
        "answer": "面向用户的完整回答（3-6 句话）",
        "confidence": 0.85,
        "evidence": [
            {"source": "本地文档 id=1", "quote": "原文证据片段"},
        ],
    },
}


# ---------------------------------------------------------------------------
# 注册到 ai_provider
# ---------------------------------------------------------------------------

RAG_TASK_TYPES: tuple[str, ...] = (
    "rag_query_job",
    "rag_query_skill",
    "rag_query_match_explain",
    "rag_query_interview_hint",
    "rag_query_knowledge_base",
)


def register_rag_tasks() -> None:
    """把 5 个 RAG task_type 注册到 ai_provider。幂等。"""
    if "rag_query_job" in TASK_DEFINITIONS:
        return

    TASK_DEFINITIONS["rag_query_job"] = JOB_DEFINITION
    TASK_DEFINITIONS["rag_query_skill"] = SKILL_DEFINITION
    TASK_DEFINITIONS["rag_query_match_explain"] = MATCH_EXPLAIN_DEFINITION
    TASK_DEFINITIONS["rag_query_interview_hint"] = INTERVIEW_HINT_DEFINITION
    TASK_DEFINITIONS["rag_query_knowledge_base"] = KNOWLEDGE_BASE_DEFINITION

    # 扩展 SUPPORTED_TASKS（原始是 tuple，需要替换为新 tuple）
    import app.services.ai_provider as _ai_module

    if "rag_query_job" not in _ai_module.SUPPORTED_TASKS:
        _ai_module.SUPPORTED_TASKS = _ai_module.SUPPORTED_TASKS + RAG_TASK_TYPES
    _ai_module._SUPPORTED_TASKS_FROZEN = False


# ---------------------------------------------------------------------------
# 用户 prompt 构造（拼接 hits）
# ---------------------------------------------------------------------------


def build_hits_block(hits: list[Hit]) -> str:
    """把检索命中序列化成可读片段，供 LLM 引用。"""
    if not hits:
        return "（本次检索未返回任何片段）"
    lines = []
    for idx, hit in enumerate(hits, start=1):
        meta = hit.metadata or {}
        title_bits = []
        for key in ("job_name", "skill_name", "candidate_name", "domain", "level", "relation_type"):
            value = meta.get(key)
            if value:
                title_bits.append(f"{key}={value}")
        title = " · ".join(title_bits) if title_bits else ""
        header = f"[{idx}] source_type={hit.source_type} ref_id={hit.ref_id} score={hit.score:.3f}"
        if title:
            header += f" | {title}"
        text = (hit.text or "").strip()
        if len(text) > 600:
            text = text[:600] + "..."
        lines.append(header)
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()


def build_user_payload(
    question: str,
    hits: list[Hit],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "question": question,
        "evidence_count": len(hits),
        "evidence_block": build_hits_block(hits),
    }
    if extra:
        payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# mock 模式下的兜底输出（与 ai_provider.analyze_with_mock 对齐）
# ---------------------------------------------------------------------------


def rag_mock_result(task_type: str, hits: list[Hit], payload: dict[str, Any]) -> dict[str, Any]:
    """RAG 场景在 mock provider 下的保底响应，避免演示时无证据可引。"""
    question = str(payload.get("question") or "")
    evidence = []
    for hit in hits[:3]:
        evidence.append(
            {
                "source": f"{hit.source_type} id={hit.ref_id}",
                "quote": (hit.text or "")[:120],
            }
        )
    if not evidence:
        evidence = [{"source": "mock", "quote": "（mock 模式未检索到片段）"}]

    if task_type == "rag_query_job":
        return {
            "summary": f"基于 {len(hits)} 条检索片段回答：{question}",
            "answer": f"（mock）已从岗位 JD 中召回 {len(hits)} 条相关片段，可作为回答依据。",
            "confidence": 0.6 if hits else 0.0,
            "evidence": evidence,
        }
    if task_type == "rag_query_skill":
        return {
            "summary": f"对技能问题的回答：{question}",
            "answer": f"（mock）已从技能图谱中召回 {len(hits)} 条相关片段。",
            "confidence": 0.6 if hits else 0.0,
            "evidence": evidence,
        }
    if task_type == "rag_query_match_explain":
        return {
            "summary": "（mock）人岗匹配差距解释",
            "answer": "（mock）已根据缺失技能和 JD 证据生成差距解释。",
            "missing_skills": list((payload.get("extra") or {}).get("missing_skills") or []),
            "confidence": 0.6 if hits else 0.0,
            "evidence": evidence,
        }
    if task_type == "rag_query_interview_hint":
        return {
            "summary": f"（mock）对 {payload.get('focus_skill', '')} 的面试追问策略",
            "answer": "（mock）已基于岗位要求生成 3-5 个深挖追问点。",
            "hints": [
                {
                    "level": "基础",
                    "question": f"请介绍一下 {payload.get('focus_skill', '该技能')} 的核心原理。",
                    "intent": "考察概念掌握",
                    "evidence_quote": (hits[0].text if hits else "")[:80],
                },
                {
                    "level": "项目",
                    "question": "请分享一个你使用该技能解决实际问题的案例。",
                    "intent": "考察落地能力",
                    "evidence_quote": (hits[0].text if hits else "")[:80] if hits else "",
                },
            ],
            "confidence": 0.6 if hits else 0.0,
            "evidence": evidence,
        }
    if task_type == "rag_query_knowledge_base":
        return {
            "summary": f"（mock）基于本地知识库证据回答：{question}",
            "answer": f"（mock）已从本地知识库召回 {len(hits)} 条相关片段，可作为回答依据。",
            "confidence": 0.6 if hits else 0.0,
            "evidence": evidence,
        }
    raise AIProviderError(f"未知 RAG 任务：{task_type}")


def analyze_rag(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """RAG 问答统一入口：mock/无 key 走 rag_mock_result，否则走真实 LLM。

    不依赖 install_mock_patch 的 monkeypatch（它对 `from ... import` 的旧引用无效），
    这里显式判断 provider 与 key，确保降级路径可靠。
    """
    import app.services.ai_provider as ai_module

    clean = {k: v for k, v in payload.items() if k != "_rag_hits"}
    if ai_module.AI_PROVIDER == "mock" or not ai_module.AI_API_KEY:
        hits = payload.get("_rag_hits") or []
        result = rag_mock_result(task_type, hits, clean)
        return {
            "provider": "mock",
            "model": "mock-llm",
            "task_type": task_type,
            "result": result,
        }
    return ai_module.analyze_with_openai_compatible(task_type, clean)


# ---------------------------------------------------------------------------
# 启动时一次性把 _original_analyze_with_mock 保留下来（占位，避免循环依赖）
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 对 ai_provider.analyze_with_ai 打补丁，让 RAG task 走 rag_mock_result
# ---------------------------------------------------------------------------


_original_analyze_with_ai = None  # 占位：install_mock_patch 会重新赋值
_original_analyze_with_mock = None


def install_mock_patch() -> None:
    """给 RAG task 打补丁：mock 或无 key 时走 rag_mock_result，否则走真实 LLM。幂等。"""
    import app.services.ai_provider as _ai_module

    if getattr(_ai_module, "_rag_patched", False):
        return

    _original_analyze_with_ai = _ai_module.analyze_with_ai
    _original_analyze_with_mock = _ai_module.analyze_with_mock

    def _patched_analyze_with_ai(task_type, payload):
        if task_type in RAG_TASK_TYPES:
            clean_payload = {k: v for k, v in payload.items() if k != "_rag_hits"}
            # 仅在 mock 模式或未配置 key 时走 rag_mock_result；否则交给真实 LLM
            if _ai_module.AI_PROVIDER == "mock" or not _ai_module.AI_API_KEY:
                hits = payload.get("_rag_hits") or []
                result = rag_mock_result(task_type, hits, clean_payload)
                return {
                    "provider": "mock",
                    "model": "mock-llm",
                    "task_type": task_type,
                    "result": result,
                }
            return _original_analyze_with_ai(task_type, clean_payload)
        return _original_analyze_with_ai(task_type, payload)

    _ai_module.analyze_with_ai = _patched_analyze_with_ai
    _ai_module.analyze_with_mock = _patched_analyze_with_ai  # 防止 analyze_with_ai 二次调用旧版
    _ai_module._rag_patched = True  # type: ignore[attr-defined]