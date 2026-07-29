from fastapi.testclient import TestClient
from sqlalchemy import delete
from uuid import uuid4

from app.main import app
from app.db.database import SessionLocal
from app.db.init_db import seed_database
from app.models import InterviewSession, InterviewTurn


seed_database()
client = TestClient(app)


def delete_interview_session(session_id: int) -> None:
    with SessionLocal() as db:
        db.execute(delete(InterviewTurn).where(InterviewTurn.session_id == session_id))
        db.execute(delete(InterviewSession).where(InterviewSession.id == session_id))
        db.commit()


def solve_captcha(question: str) -> str:
    left, operator, right, *_ = question.split()
    if operator == "+":
        return str(int(left) + int(right))
    if operator == "-":
        return str(int(left) - int(right))
    return str(int(left) * int(right))


def test_overview_summary():
    response = client.get("/api/overview/summary")
    assert response.status_code == 200
    assert response.json()["job_count"] >= 10


def test_jd_parse():
    text = "大模型应用工程师，需要 Python、RAG、LangChain、向量数据库 和 Docker。"
    response = client.post("/api/jd/parse", json={"text": text})
    assert response.status_code == 200
    assert response.json()["job_name"] == "大模型应用工程师"


def test_all_ai_business_routes_use_provider():
    status = client.get("/api/ai/status")
    assert status.status_code == 200
    assert len(status.json()["supported_tasks"]) == 6

    emerging = client.get("/api/emerging-jobs")
    assert emerging.status_code == 200
    assert len(emerging.json()) == 5
    assert all(item["ai_provider"] == "mock" for item in emerging.json())

    interview_login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    interview_headers = {"Authorization": f"Bearer {interview_login.json()['token']}"}
    learning = client.get("/api/learning-path/1", headers=interview_headers)
    assert learning.status_code == 200
    assert learning.json()["items"]
    assert learning.json()["ai_provider"] == "mock"

    interview = client.post(
        "/api/digital-interviewer/interview",
        headers=interview_headers,
        json={"job_name": "数据分析师", "resume_summary": "熟悉 SQL", "candidate_answer": "", "stage": "opening", "action": "start"},
    )
    assert interview.status_code == 200
    assert interview.json()["result"]["next_question"]
    delete_interview_session(interview.json()["interview_session"]["id"])

    login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    resume = client.post(
        "/api/resume/parse",
        headers=headers,
        json={"text": "姓名：林一，本科，熟悉 Python 和 SQL。"},
    )
    assert resume.status_code == 200
    assert resume.json()["ai_provider"] == "mock"
    assert resume.json()["resume_id"] > 0

    match = client.post(
        "/api/match-analysis",
        headers=headers,
        json={"resume_id": resume.json()["resume_id"], "target_job_id": 1},
    )
    assert match.status_code == 200
    assert match.json()["ai_analysis"]["summary"]


def test_interview_history_is_persisted_and_resumable():
    login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}

    opening = client.post(
        "/api/digital-interviewer/interview",
        headers=headers,
        json={
            "job_name": "AI 应用开发工程师",
            "resume_summary": "做过 RAG 知识库项目",
            "interview_style": "project",
            "action": "start",
        },
    )
    assert opening.status_code == 200
    session_id = opening.json()["interview_session"]["id"]
    assert len(opening.json()["history"]) == 1

    follow_up = client.post(
        "/api/digital-interviewer/interview",
        headers=headers,
        json={
            "job_name": "AI 应用开发工程师",
            "interview_session_id": session_id,
            "candidate_answer": "我用 RAG 做了知识库，并把召回率提升到 85%。",
            "action": "answer",
        },
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["interview_session"]["round_count"] == 1
    assert len(follow_up.json()["history"]) == 2
    assert follow_up.json()["history"][0]["answer"]
    assert "检索" in follow_up.json()["result"]["next_question"]

    skipped = client.post(
        "/api/digital-interviewer/interview",
        headers=headers,
        json={
            "job_name": "AI 应用开发工程师",
            "interview_session_id": session_id,
            "action": "skip",
        },
    )
    assert skipped.status_code == 200
    assert skipped.json()["interview_session"]["round_count"] == 1
    assert len(skipped.json()["history"]) == 3
    assert skipped.json()["history"][1]["answer"] == "（已跳过）"

    sessions = client.get("/api/digital-interviewer/sessions", headers=headers)
    assert sessions.status_code == 200
    assert any(row["id"] == session_id for row in sessions.json())

    detail = client.get(f"/api/digital-interviewer/sessions/{session_id}", headers=headers)
    assert detail.status_code == 200
    assert len(detail.json()["history"]) == 3

    completed = client.post(f"/api/digital-interviewer/sessions/{session_id}/complete", headers=headers)
    assert completed.status_code == 200
    assert completed.json()["session"]["status"] == "completed"
    assert completed.json()["final_report"]["overall_score"] > 0
    assert completed.json()["final_report"]["rounds_scored"] == 1
    assert set(completed.json()["final_report"]["dimension_scores"]) == {"专业能力", "项目表达", "岗位匹配", "逻辑沟通"}

    completed_detail = client.get(f"/api/digital-interviewer/sessions/{session_id}", headers=headers)
    assert completed_detail.json()["session"]["final_score"] == completed.json()["final_report"]["overall_score"]
    delete_interview_session(session_id)


def test_hr_login_and_candidate_list():
    response = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json()["user"]["role"] == "hr"

    candidates = client.get("/api/hr/candidates", headers={"Authorization": f"Bearer {token}"})
    assert candidates.status_code == 200
    assert len(candidates.json()) >= 1


def test_candidate_profile_update_and_role_guard():
    response = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    assert response.status_code == 200
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.put(
        "/api/profile/me",
        headers=headers,
        json={
            "real_name": "Demo Student",
            "education": "本科",
            "major": "数据科学",
            "school": "示例大学",
            "target_role": "数据分析师",
            "city": "上海",
            "expected_salary": "12k-16k",
            "skills": ["Python", "SQL", "数据可视化"],
            "certificates": ["CET-6"],
            "projects": ["校园招聘数据分析项目"],
            "internships": ["数据运营实习"],
            "awards": ["数学建模竞赛"],
            "self_summary": "关注数据分析和业务洞察。",
        },
    )
    assert profile.status_code == 200
    assert profile.json()["completeness"] > 80

    forbidden = client.get("/api/hr/candidates", headers=headers)
    assert forbidden.status_code == 403


def test_candidate_resume_scope_and_match_guard():
    hr_login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
    candidate_login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    assert hr_login.status_code == 200
    assert candidate_login.status_code == 200

    hr_headers = {"Authorization": f"Bearer {hr_login.json()['token']}"}
    candidate = candidate_login.json()["user"]
    candidate_headers = {"Authorization": f"Bearer {candidate_login.json()['token']}"}

    all_resumes = client.get("/api/resumes", headers=hr_headers)
    own_resumes = client.get("/api/resumes", headers=candidate_headers)
    assert all_resumes.status_code == 200
    assert own_resumes.status_code == 200
    assert all(row["user_id"] == candidate["id"] for row in own_resumes.json())

    foreign = next((row for row in all_resumes.json() if row["user_id"] != candidate["id"]), None)
    assert foreign is not None
    blocked = client.post(
        "/api/match-analysis",
        headers=candidate_headers,
        json={"resume_id": foreign["id"], "target_job_id": 1},
    )
    assert blocked.status_code == 403


def test_match_report_is_persisted_and_drives_learning_path():
    login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    match = client.post(
        "/api/match-analysis",
        headers=headers,
        json={
            "resume": {
                "name": "测试候选人",
                "skills": ["Python", "SQL", "Docker"],
                "projects": ["使用 Python 和 SQL 完成数据服务，Docker 部署后接口耗时降低 20%"],
                "internships": ["参与数据平台需求分析与接口开发"],
                "certificates": [],
            },
            "target_job_id": 1,
        },
    )
    assert match.status_code == 200
    report_id = match.json()["report_id"]
    assert report_id > 0
    assert match.json()["scoring_version"] == "evidence-v2"
    assert all("evidence" in row for row in match.json()["dimension_rows"])

    history = client.get("/api/match-analysis/history", headers=headers)
    assert history.status_code == 200
    assert any(item["report_id"] == report_id for item in history.json())

    detail = client.get(f"/api/match-analysis/{report_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["total_score"] == match.json()["total_score"]

    learning = client.get(f"/api/learning-path/{report_id}", headers=headers)
    assert learning.status_code == 200
    assert learning.json()["report_id"] == report_id
    assert learning.json()["target_job"] == match.json()["target_job"]


def test_register_with_rules_and_math_captcha():
    captcha = client.get("/api/auth/captcha")
    assert captcha.status_code == 200
    captcha_data = captcha.json()
    username = f"u{uuid4().hex[:7]}1"
    payload = {
        "username": username,
        "password": "abc12345",
        "confirm_password": "abc12345",
        "role": "candidate",
        "display_name": "测试用户",
        "email": "demo2026@example.com",
        "organization": "示例学校",
        "captcha_token": captcha_data["token"],
        "captcha_answer": solve_captcha(captcha_data["question"]),
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["user"]["username"] == username


def test_register_rejects_invalid_username():
    captcha_data = client.get("/api/auth/captcha").json()
    response = client.post(
        "/api/auth/register",
        json={
            "username": "abcdef",
            "password": "abc12345",
            "confirm_password": "abc12345",
            "role": "candidate",
            "display_name": "测试用户",
            "email": "bad-name@example.com",
            "captcha_token": captcha_data["token"],
            "captcha_answer": solve_captcha(captcha_data["question"]),
        },
    )
    assert response.status_code == 400
