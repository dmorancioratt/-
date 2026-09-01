import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.services.mock_llm import mock_extract_jd, mock_resume_parse
from app.services.constants import JOB_NAMES, JOB_PROFILES

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass


AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek").strip().lower()
AI_API_BASE_URL = (
    os.getenv("DEEPSEEK_API_BASE_URL")
    or os.getenv("AI_API_BASE_URL")
    or "https://api.deepseek.com"
).rstrip("/")
AI_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("AI_API_KEY") or ""
AI_MODEL = os.getenv("DEEPSEEK_MODEL") or os.getenv("AI_MODEL") or "deepseek-v4-flash"
AI_TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT_SECONDS", "90"))
AI_MAX_RETRIES = max(0, int(os.getenv("AI_MAX_RETRIES", "2")))
APP_ENV = os.getenv("APP_ENV", "production").strip().lower()

SUPPORTED_TASKS = (
    "jd_parse",
    "resume_parse",
    "match_analysis",
    "learning_path",
    "emerging_job_analysis",
    "digital_interview",
    "workflow_rag_answer",
)

TASK_DEFINITIONS: dict[str, dict[str, Any]] = {
    "jd_parse": {
        "instruction": "从 input.text 的岗位 JD 原文中抽取事实。若原文明确出现岗位名称，job_name 必须原样提取且不得留空；domain 可根据岗位名称和职责归类。不得补写原文没有的硬性要求。confidence 必须是 0 到 1 的小数，evidence 的 quote 必须来自输入原文。",
        "example": {
            "job_name": "岗位名称",
            "domain": "所属领域",
            "level": "初级/中级/高级/专家/未说明",
            "responsibilities": ["职责"],
            "required_skills": ["必备技能"],
            "preferred_skills": ["加分技能"],
            "tools": ["工具或平台"],
            "certificates": ["证书"],
            "experience": "经验要求或未说明",
            "scenarios": ["业务场景"],
            "confidence": 0.9,
            "evidence": [{"source": "JD 原文", "quote": "原文证据片段"}],
        },
    },
    "resume_parse": {
        "instruction": "从简历原文抽取信息。没有出现的信息用空字符串或空数组，禁止虚构学校、项目、证书和技能等级。",
        "example": {
            "name": "姓名",
            "education": "最高学历",
            "major": "专业",
            "school": "学校",
            "projects": ["项目名称或简短项目描述"],
            "internships": ["实习经历"],
            "skills": [{"name": "技能", "level": "基础/中级/高级/未说明"}],
            "certificates": ["证书"],
            "competitions": ["竞赛或奖项"],
            "intention": "岗位意向",
        },
    },
    "match_analysis": {
        "instruction": "基于给定的确定性评分、逐维度证据、候选人经历和岗位要求解释匹配结果。不得篡改输入中的分数；每个判断都必须引用输入中已有的技能或经历，不得编造。建议要具体、可执行，并分别覆盖简历修改、能力补齐和面试准备。",
        "example": {
            "summary": "综合匹配结论",
            "verdict": "推荐进入面试/建议补强后再投递/暂不匹配",
            "suggestions": ["具体提升建议"],
            "risk_points": ["证据不足或岗位差距"],
            "dimension_insights": [
                {
                    "dimension": "必备技能",
                    "finding": "基于评分与证据的判断",
                    "evidence": ["输入中已有的证据"],
                    "action": "下一步行动",
                }
            ],
            "resume_rewrites": ["可以直接用于改写简历的表达建议"],
            "interview_focus": ["建议重点准备的面试问题"],
            "confidence_note": "说明当前结论的数据充分程度",
        },
    },
    "learning_path": {
        "instruction": "围绕缺失技能生成循序渐进且可以执行的学习路径，优先复用输入中的建议阶段，每阶段必须有可验证产出。",
        "example": {
            "summary": "路径设计说明",
            "note": "面向用户的简短建议",
            "stages": ["阶段名称"],
            "items": [
                {
                    "stage": "阶段名称",
                    "content": "学习内容",
                    "project": "可验证的练习或项目产出",
                    "duration": "预计周期",
                    "prerequisites": ["前置技能或阶段"],
                }
            ],
        },
    },
    "emerging_job_analysis": {
        "instruction": "批量分析输入中的候选新岗位。只能基于随请求提供的候选数据和证据进行归纳，不得声称已实时检索外部网站。每个输入候选岗位都应返回一项。",
        "example": {
            "items": [
                {
                    "job_name": "候选岗位",
                    "emerging_index": 0.8,
                    "related_skills": ["关联技能"],
                    "main_sources": ["输入中给出的来源"],
                    "definition": "岗位定义",
                    "responsibilities": ["核心职责"],
                    "required_skills": ["必备技能"],
                    "preferred_skills": ["加分技能"],
                    "scenarios": ["应用场景"],
                    "review_status": "approved/pending",
                    "evidence": [{"source": "来源", "quote": "证据"}],
                }
            ]
        },
    },
    "digital_interview": {
        "instruction": (
            "扮演自然、专业且会倾听的面试官。必须结合 history 中的完整对话和候选人刚才回答，"
            "优先追问对方实际提到的项目、技术选择、困难、取舍和结果，禁止重复已经问过的问题。"
            "每轮只问一个清晰问题，在深挖与换方向之间自然切换，并遵循 interview_style。"
            "feedback 用一到两句话指出回答中具体做得好的地方和一个可改进点，不说空话；"
            "action 为 skip 时自然换一个考察方向且不扣分。只评价岗位相关能力。"
        ),
        "example": {
            "interviewer_name": "数融面试官",
            "next_question": "下一道问题",
            "follow_up_basis": "追问依据",
            "feedback": "简短反馈",
            "score_preview": {"专业能力": 75, "项目表达": 75, "岗位匹配": 75, "逻辑沟通": 75},
            "follow_up_tags": ["追问标签"],
        },
    },
    "workflow_rag_answer": {
        "instruction": (
            "仅依据 input.evidence_block 中的用户知识库原文回答 input.question。"
            "若证据不足，必须明确说明无法从当前知识库得出结论，不得使用外部常识补写。"
            "answer 应简洁直接；confidence 必须反映证据充分程度；evidence 中的 quote 必须逐字来自 evidence_block。"
        ),
        "example": {
            "answer": "基于知识库证据的回答",
            "confidence": 0.85,
            "evidence": [{"source": "user_docs id=1", "quote": "知识库原文片段"}],
        },
    },
}


class AIProviderError(RuntimeError):
    pass


def ai_status() -> dict[str, Any]:
    configured = bool(AI_API_BASE_URL and AI_API_KEY)
    return {
        "provider": AI_PROVIDER,
        "model": AI_MODEL,
        "base_url_configured": bool(AI_API_BASE_URL),
        "api_key_configured": bool(AI_API_KEY),
        "enabled": AI_PROVIDER != "mock" and configured,
        "json_output": AI_PROVIDER != "mock",
        "supported_tasks": list(SUPPORTED_TASKS),
    }


def analyze_with_ai(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if task_type not in SUPPORTED_TASKS:
        raise AIProviderError(f"不支持的 AI 任务：{task_type}")
    if AI_PROVIDER == "mock":
        if APP_ENV != "test":
            raise AIProviderError("模拟 AI 仅允许在自动化测试环境使用，请配置真实 AI 服务")
        return analyze_with_mock(task_type, payload)
    if AI_PROVIDER not in {"deepseek", "openai_compatible"}:
        raise AIProviderError(f"不支持的 AI Provider：{AI_PROVIDER}")
    return analyze_with_openai_compatible(task_type, payload)


def analyze_with_mock(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or payload.get("jd_text") or payload.get("resume_text") or "")
    if task_type == "jd_parse":
        result = mock_extract_jd(text)
    elif task_type == "resume_parse":
        result = mock_resume_parse(text)
    elif task_type == "match_analysis":
        missing = _string_list(payload.get("missing_skills"))
        result = {
            "summary": "当前画像与目标岗位有一定关联，建议优先补齐缺失技能并增加可验证的项目证据。",
            "verdict": "建议补强后再投递",
            "suggestions": [f"围绕 {skill} 完成一个可展示的小项目。" for skill in missing[:5]],
            "risk_points": ["部分能力只有技能名称，缺少项目结果作为证据。"],
            "dimension_insights": [],
            "resume_rewrites": ["使用“背景—个人行动—量化结果”的结构重写最相关项目经历。"],
            "interview_focus": [f"准备说明如何在真实项目中使用 {skill}。" for skill in missing[:3]],
            "confidence_note": "结论基于当前已填写的技能和经历，资料越完整可信度越高。",
        }
    elif task_type == "learning_path":
        suggested = payload.get("suggested_stages") or []
        result = {
            "summary": "根据岗位差距生成分阶段提升路线。",
            "note": "先补齐关键基础，再通过项目和部署形成可验证证据。",
            "stages": [str(item.get("stage", "")) for item in suggested if isinstance(item, dict)],
            "items": suggested,
        }
    elif task_type == "emerging_job_analysis":
        result = {"items": payload.get("candidates") or []}
    elif task_type == "workflow_rag_answer":
        evidence = payload.get("retrieved_evidence") or []
        result = {
            "answer": evidence[0].get("text", "") if evidence else "当前知识库没有可用于回答的证据。",
            "confidence": 0.6 if evidence else 0.0,
            "evidence": [
                {
                    "source": f"user_docs id={item.get('ref_id')}",
                    "quote": str(item.get("text") or "")[:200],
                }
                for item in evidence[:3]
            ],
        }
    else:
        answer = _string(payload.get("candidate_answer"))
        action = _string(payload.get("action"), "answer")
        style = _string(payload.get("interview_style"), "adaptive")
        round_number = max(1, int(payload.get("round_number") or 1))
        opening_questions = {
            "adaptive": "先从你最熟悉的经历开始吧。请介绍一个最能体现你与这个岗位匹配度的项目。",
            "project": "请挑一个你投入最多的项目，先说清楚目标、你的职责和最后的结果。",
            "scenario": "假设你刚接手一个目标不清、数据也不完整的任务，你会怎样推进第一周的工作？",
            "conversational": "我们轻松一点开始：你为什么想做这个岗位，哪段经历最影响这个选择？",
        }
        fallback_questions = [
            "如果让你重新做一次刚才的工作，你会优先改变哪个决定？为什么？",
            "这段经历里最棘手的意外是什么？你当时如何判断和处理？",
            "你怎样验证自己的方案确实解决了问题，而不只是完成了任务？",
            "当团队成员不同意你的方案时，你通常怎样推动形成结论？",
            "把这个经验迁移到更大规模的场景，最先出现的风险会是什么？",
            "结合目标岗位，你认为自己目前最需要补强的能力是什么？准备怎样补？",
        ]
        lowered = answer.lower()
        if not answer or action == "start":
            question = opening_questions.get(style, opening_questions["adaptive"])
            basis = "根据面试风格和目标岗位建立自然开场。"
            feedback = "我们从你熟悉的内容开始。"
        elif action == "skip":
            question = fallback_questions[(round_number - 1) % len(fallback_questions)]
            basis = "候选人选择跳过，切换到新的能力维度。"
            feedback = "本题已跳过，不影响评价。"
        elif "rag" in lowered or "检索" in answer or "知识库" in answer:
            question = "你刚才提到了检索或知识库。线上出现‘检索到了但回答仍然不准’时，你会怎样定位是召回、排序还是生成环节的问题？"
            basis = "基于回答中提到的 RAG/检索场景继续深挖诊断能力。"
            feedback = "你给出了明确的技术方向；下一步可以进一步说明判断依据和验证指标。"
        elif "sql" in lowered or "数据库" in answer:
            question = "你提到了 SQL 或数据库。如果核心查询突然慢了十倍，你会按什么顺序排查，并如何确认优化没有改变业务口径？"
            basis = "基于回答中的数据库经验追问性能与业务准确性。"
            feedback = "回答体现了数据处理经验；可以补充一次具体问题的定位过程和最终效果。"
        elif "python" in lowered:
            question = "你提到了 Python。请讲一次代码从‘能运行’变成‘可维护、可上线’的改造，你具体做了哪些取舍？"
            basis = "基于回答中的 Python 经验追问工程化能力。"
            feedback = "技术栈表达清楚；如果能补充代码规模、协作方式和结果会更有说服力。"
        else:
            question = fallback_questions[(round_number - 1) % len(fallback_questions)]
            basis = "根据当前轮次切换能力维度，避免重复模板化追问。"
            feedback = (
                "回答有明确内容，也提供了可量化信息；建议再说明这些结果与你个人行动之间的关系。"
                if any(char.isdigit() for char in answer)
                else "回答方向清楚；建议补充一个具体行动、当时的判断依据和可验证结果。"
            )
        answer_score = min(88, 62 + len(answer) // 8 + (6 if any(char.isdigit() for char in answer) else 0)) if answer else 0
        result = {
            "interviewer_name": "数融面试官",
            "next_question": question,
            "follow_up_basis": basis,
            "feedback": feedback,
            "score_preview": {
                "专业能力": answer_score,
                "项目表达": max(0, answer_score - 3),
                "岗位匹配": max(0, answer_score - 1),
                "逻辑沟通": min(92, answer_score + 2),
            },
            "follow_up_tags": [],
        }
    return {"provider": "mock", "model": "mock-llm", "task_type": task_type, "result": _normalize_result(task_type, result, payload)}


def analyze_with_openai_compatible(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not AI_API_BASE_URL or not AI_API_KEY:
        raise AIProviderError("DeepSeek 接口未配置，请检查 DEEPSEEK_API_BASE_URL 和 DEEPSEEK_API_KEY")

    prompt = build_prompt(task_type, payload)
    body: dict[str, Any] = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是岗位能力图谱与人岗匹配分析助手。必须仅输出一个有效 JSON 对象，不要输出 Markdown、代码围栏或额外说明。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
    }
    if AI_PROVIDER == "deepseek":
        body["thinking"] = {"type": "disabled"}

    last_error: Exception | None = None
    for attempt in range(AI_MAX_RETRIES + 1):
        try:
            data = _post_chat_completion(body)
            content = _extract_content(data)
            result = _parse_json_object(content)
            normalized = _normalize_result(task_type, result, payload)
            return {
                "provider": AI_PROVIDER,
                "model": data.get("model") or AI_MODEL,
                "task_type": task_type,
                "result": normalized,
                "usage": data.get("usage") or {},
            }
        except AIProviderError as exc:
            last_error = exc
            if attempt >= AI_MAX_RETRIES or not _is_retryable(exc):
                break
            time.sleep(0.5 * (attempt + 1))

    raise last_error or AIProviderError("DeepSeek 接口调用失败")


def _post_chat_completion(body: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{AI_API_BASE_URL}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "SkillBridge-Graph/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=AI_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = _read_http_error(exc)
        raise AIProviderError(f"DeepSeek 接口返回 HTTP {exc.code}：{message}") from exc
    except urllib.error.URLError as exc:
        raise AIProviderError(f"DeepSeek 网络连接失败：{exc.reason}") from exc
    except TimeoutError as exc:
        raise AIProviderError("DeepSeek 接口调用超时") from exc
    except json.JSONDecodeError as exc:
        raise AIProviderError("DeepSeek 接口返回了无法解析的响应") from exc


def _read_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        data = json.loads(exc.read().decode("utf-8"))
        message = data.get("error", {}).get("message") or data.get("message")
        if message:
            return str(message)[:300]
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        pass
    return "请求未成功，请检查密钥、余额、模型名称或请求频率"


def _extract_content(data: dict[str, Any]) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIProviderError("DeepSeek 响应缺少 choices.message.content") from exc
    if not isinstance(content, str) or not content.strip():
        raise AIProviderError("DeepSeek 返回了空内容")
    return content.strip()


def _parse_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIProviderError("DeepSeek 未返回有效 JSON") from exc
    if not isinstance(parsed, dict):
        raise AIProviderError("DeepSeek 返回的 JSON 顶层必须是对象")
    return parsed


def _is_retryable(exc: AIProviderError) -> bool:
    message = str(exc)
    return any(token in message for token in ("HTTP 429", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "网络连接失败", "调用超时", "空内容", "有效 JSON"))


def build_prompt(task_type: str, payload: dict[str, Any]) -> str:
    definition = TASK_DEFINITIONS[task_type]
    return json.dumps(
        {
            "task": task_type,
            "instruction": definition["instruction"],
            "rules": [
                "输出必须是一个有效 JSON 对象。",
                "严格使用 example_json 的字段结构，不要增加解释性外层。",
                "所有面向用户的文本使用简体中文；技术名词可保留英文。",
                "数组无内容时返回空数组，未知字符串返回空字符串，不得编造事实。",
            ],
            "example_json": definition["example"],
            "input": payload,
        },
        ensure_ascii=False,
    )


def _normalize_result(task_type: str, result: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    if task_type == "jd_parse":
        evidence = _evidence_list(result.get("evidence") or result.get("evidence_sources"))
        source_text = _string(payload.get("text"))
        job_name = _string(result.get("job_name")) or _infer_job_name(source_text)
        profile = JOB_PROFILES.get(job_name, {})
        return {
            "job_name": job_name or "未识别岗位",
            "domain": _string(result.get("domain")) or _string(profile.get("domain"), "未分类"),
            "level": _string(result.get("level"), "未说明"),
            "responsibilities": _string_list(result.get("responsibilities")),
            "required_skills": _string_list(result.get("required_skills")),
            "preferred_skills": _string_list(result.get("preferred_skills")),
            "tools": _string_list(result.get("tools")),
            "certificates": _string_list(result.get("certificates")),
            "experience": _string(result.get("experience"), "未说明"),
            "scenarios": _string_list(result.get("scenarios")),
            "confidence": _ratio(result.get("confidence"), 0.5),
            "evidence": evidence,
        }
    if task_type == "resume_parse":
        source_text = _string(payload.get("text"))
        skills = []
        for item in _list(result.get("skills")):
            if isinstance(item, dict):
                name = _string(item.get("name"))
                if name:
                    skills.append({"name": name, "level": _string(item.get("level"), "未说明")})
            elif _string(item):
                skills.append({"name": _string(item), "level": "未说明"})
        return {
            "name": _first_string(result, "name", "full_name", "candidate_name") or _extract_labeled_value(source_text, ("姓名", "Name")),
            "education": _first_string(result, "education", "education_level") or _infer_education(source_text),
            "major": _first_string(result, "major", "field_of_study") or _extract_labeled_value(source_text, ("专业",)),
            "school": _first_string(result, "school", "school_name", "university") or _extract_labeled_value(source_text, ("学校", "院校")),
            "projects": _experience_list(result.get("projects")),
            "internships": _experience_list(result.get("internships")),
            "skills": skills,
            "certificates": _string_list(result.get("certificates")),
            "competitions": _experience_list(result.get("competitions")),
            "intention": _first_string(result, "intention", "target_job", "job_intention"),
        }
    if task_type == "match_analysis":
        insights = []
        for item in _list(result.get("dimension_insights")):
            if not isinstance(item, dict):
                continue
            dimension = _string(item.get("dimension"))
            finding = _string(item.get("finding"))
            if not dimension and not finding:
                continue
            insights.append(
                {
                    "dimension": dimension,
                    "finding": finding,
                    "evidence": _string_list(item.get("evidence")),
                    "action": _string(item.get("action")),
                }
            )
        return {
            "summary": _string(result.get("summary"), "已根据岗位要求和候选人能力完成综合分析。"),
            "verdict": _string(result.get("verdict"), "建议结合证据完整度进行人工复核"),
            "suggestions": _string_list(result.get("suggestions")),
            "risk_points": _string_list(result.get("risk_points")),
            "dimension_insights": insights,
            "resume_rewrites": _string_list(result.get("resume_rewrites")),
            "interview_focus": _string_list(result.get("interview_focus")),
            "confidence_note": _string(result.get("confidence_note")),
        }
    if task_type == "learning_path":
        items = []
        source_items = result.get("items") or payload.get("suggested_stages") or []
        for item in _list(source_items):
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "stage": _string(item.get("stage"), "学习阶段"),
                    "content": _string(item.get("content")),
                    "project": _string(item.get("project")),
                    "duration": _string(item.get("duration")),
                    "prerequisites": _string_list(item.get("prerequisites")),
                }
            )
        return {
            "summary": _string(result.get("summary"), "已根据能力差距生成学习路径。"),
            "note": _string(result.get("note"), "建议按阶段完成学习和项目产出。"),
            "stages": _string_list(result.get("stages")) or [item["stage"] for item in items],
            "items": items,
        }
    if task_type == "emerging_job_analysis":
        fallback_by_name = {
            str(item.get("job_name")): item
            for item in _list(payload.get("candidates"))
            if isinstance(item, dict) and item.get("job_name")
        }
        items = []
        for raw in _list(result.get("items")):
            if not isinstance(raw, dict):
                continue
            fallback = fallback_by_name.get(str(raw.get("job_name")), {})
            merged = {**fallback, **raw}
            items.append(
                {
                    "job_name": _string(merged.get("job_name"), "未命名候选岗位"),
                    "emerging_index": _ratio(merged.get("emerging_index"), 0.5),
                    "related_skills": _string_list(merged.get("related_skills")),
                    "main_sources": _string_list(merged.get("main_sources")),
                    "definition": _string(merged.get("definition")),
                    "responsibilities": _string_list(merged.get("responsibilities")),
                    "required_skills": _string_list(merged.get("required_skills")),
                    "preferred_skills": _string_list(merged.get("preferred_skills")),
                    "scenarios": _string_list(merged.get("scenarios")),
                    "review_status": _string(merged.get("review_status"), "pending"),
                    "evidence": _evidence_list(merged.get("evidence")),
                }
            )
        return {"items": items}

    if task_type.startswith("rag_query_"):
        # RAG 问答：保留 answer/summary/confidence，evidence 由调用方根据 hits 组装
        return {
            "answer": _string(result.get("answer")),
            "summary": _string(result.get("summary")),
            "confidence": _ratio(result.get("confidence"), 0.5),
        }

    scores = result.get("score_preview") if isinstance(result.get("score_preview"), dict) else {}
    normalized_scores = {
        name: _score(scores.get(name), 0)
        for name in ("专业能力", "项目表达", "岗位匹配", "逻辑沟通")
    }
    return {
        "interviewer_name": _string(result.get("interviewer_name"), "数融面试官"),
        "next_question": _string(result.get("next_question"), "请介绍一段与目标岗位最相关的项目经历。"),
        "follow_up_basis": _string(result.get("follow_up_basis")),
        "feedback": _string(result.get("feedback"), "等待候选人回答。"),
        "score_preview": normalized_scores,
        "follow_up_tags": _string_list(result.get("follow_up_tags")),
    }


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _string_list(value: Any) -> list[str]:
    result = []
    for item in _list(value):
        text = _string(item)
        if text and text not in result:
            result.append(text)
    return result


def _experience_list(value: Any) -> list[str]:
    result = []
    for item in _list(value):
        if isinstance(item, dict):
            text = _first_string(item, "name", "title", "description", "summary")
        else:
            text = _string(item)
        if text and text not in result:
            result.append(text)
    return result


def _first_string(data: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _string(data.get(key))
        if value:
            return value
    return ""


def _extract_labeled_value(text: str, labels: tuple[str, ...]) -> str:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"(?:^|\n)\s*(?:{label_pattern})\s*[:：]\s*([^\n|，,；;]{{2,40}})",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def _infer_education(text: str) -> str:
    for education in ("博士", "硕士", "本科", "大专", "专科", "高中"):
        if education in text:
            return education
    return ""


def _evidence_list(value: Any) -> list[dict[str, str]]:
    evidence = []
    for item in _list(value):
        if not isinstance(item, dict):
            continue
        source = _string(item.get("source"), "输入文本")
        quote = _string(item.get("quote"))
        if quote:
            evidence.append({"source": source, "quote": quote})
    return evidence


def _infer_job_name(text: str) -> str:
    compact = re.sub(r"\s+", "", text).lower()
    for name in sorted(JOB_NAMES, key=len, reverse=True):
        if re.sub(r"\s+", "", name).lower() in compact:
            return name
    first_segment = re.split(r"[，。；;：:\n]", text, maxsplit=1)[0].strip()
    if 2 <= len(first_segment) <= 30 and re.search(r"(工程师|分析师|经理|顾问|专员|开发|运营|架构师|设计师)$", first_segment):
        return first_segment
    return ""


def _ratio(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number > 1:
        number /= 100
    return round(min(1.0, max(0.0, number)), 3)


def _score(value: Any, default: float) -> float:
    try:
        return round(min(100.0, max(0.0, float(value))), 1)
    except (TypeError, ValueError):
        return default
