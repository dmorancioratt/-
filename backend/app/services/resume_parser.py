from app.services.ai_provider import analyze_with_ai


def parse_resume_text(text: str) -> dict:
    return analyze_with_ai("resume_parse", {"text": text})["result"]
