import json

import pytest

from app.services import ai_provider


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


def test_deepseek_json_request_and_jd_normalization(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.headers["Authorization"]
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "model": "deepseek-v4-flash",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "job_name": "",
                                    "domain": "人工智能",
                                    "level": "中级",
                                    "responsibilities": ["建设 RAG 应用"],
                                    "required_skills": ["Python", "RAG"],
                                    "preferred_skills": [],
                                    "tools": ["Docker"],
                                    "certificates": [],
                                    "experience": "未说明",
                                    "scenarios": ["企业知识库"],
                                    "confidence": 92,
                                    "evidence": [{"source": "JD 原文", "quote": "需要 Python、RAG"}],
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ],
                "usage": {"total_tokens": 100},
            }
        )

    monkeypatch.setattr(ai_provider, "AI_PROVIDER", "deepseek")
    monkeypatch.setattr(ai_provider, "AI_API_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setattr(ai_provider, "AI_API_KEY", "test-key")
    monkeypatch.setattr(ai_provider, "AI_MODEL", "deepseek-v4-flash")
    monkeypatch.setattr(ai_provider.urllib.request, "urlopen", fake_urlopen)

    response = ai_provider.analyze_with_ai("jd_parse", {"text": "大模型应用工程师，需要 Python、RAG。"})

    assert response["provider"] == "deepseek"
    assert response["result"]["confidence"] == 0.92
    assert response["result"]["job_name"] == "大模型应用工程师"
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["thinking"] == {"type": "disabled"}
    assert captured["authorization"] == "Bearer test-key"


def test_rejects_unknown_ai_task():
    with pytest.raises(ai_provider.AIProviderError, match="不支持的 AI 任务"):
        ai_provider.analyze_with_ai("unknown_task", {})


def test_resume_normalization_falls_back_to_explicit_source_labels():
    result = ai_provider._normalize_result(
        "resume_parse",
        {
            "name": "",
            "education": "",
            "major": "",
            "school": "",
            "projects": [{"name": "企业知识库项目"}],
            "internships": [],
            "skills": ["Python"],
            "certificates": [],
            "competitions": [],
            "intention": "",
        },
        {"text": "姓名：张测试\n学历：本科\n专业：计算机科学与技术\n学校：示例大学"},
    )
    assert result["name"] == "张测试"
    assert result["education"] == "本科"
    assert result["major"] == "计算机科学与技术"
    assert result["school"] == "示例大学"
    assert result["projects"] == ["企业知识库项目"]
    assert result["skills"] == [{"name": "Python", "level": "未说明"}]


def test_rag_normalization_preserves_citations_for_guard_validation():
    result = ai_provider._normalize_result(
        "rag_query_knowledge_base",
        {
            "answer": "试用期为三个月。",
            "confidence": 0.93,
            "evidence": [{"source": "user_docs id=7", "quote": "试用期为三个月"}],
        },
        {},
    )
    assert result["evidence"] == [{"source": "user_docs id=7", "quote": "试用期为三个月"}]
