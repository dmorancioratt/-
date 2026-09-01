import json

from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from uuid import uuid4

from app.main import app
from app.db.database import SessionLocal
from app.db.init_db import seed_database
from app.models import DataSource, EvolutionEvent, InterviewSession, InterviewTurn, JobCertificateRelation, JobEntity, JobSkillRelation, ParsedJD, RawJD, ReviewTask, SkillEntity
from app.services.jd_parser import text_hash


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
    assert response.json()["market_coverage"]["source_count"] >= 8
    assert response.json()["trend"]


def test_official_market_snapshot_is_shared_and_traceable():
    login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    response = client.get("/api/market/snapshot", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["coverage"]["source_count"] >= 8
    assert payload["coverage"]["record_count"] >= 50000
    assert payload["software_revenue_trend"][-1]["period"] == "2026-05"
    assert payload["software_revenue_trend"][-1]["value"] == 62451
    assert all(source["source_url"].startswith("https://") for source in payload["sources"])
    assert any(item["name"] == "智能体开发员" for item in payload["emerging_jobs"])
    assert any(item["name"] == "计算机技术与软件专业技术资格" for item in payload["certificates"])


def test_authoritative_catalog_connects_jobs_skills_certificates_and_graph():
    jobs = client.get("/api/jobs")
    assert jobs.status_code == 200
    intelligent_agent = next(item for item in jobs.json() if item["name"] == "智能体开发员")
    assert intelligent_agent["status"] == "proposed"
    assert intelligent_agent["requirements"]["required_skills"]
    assert intelligent_agent["requirements"]["recommended_certificates"]
    assert intelligent_agent["authority"]["onet_soc_code"] == "15-1252.00"
    assert intelligent_agent["authority"]["catalog_version"] == "2026.08-authority-v2"

    graph = client.get("/api/skill-graph")
    assert graph.status_code == 200
    nodes = {item["id"]: item for item in graph.json()["nodes"]}
    certificate_ids = {node_id for node_id, node in nodes.items() if node["type"] == "Certificate"}
    assert certificate_ids
    assert all(any(edge["target"] == node_id for edge in graph.json()["edges"]) for node_id in certificate_ids)
    assert any(edge["source"] == f"job-{intelligent_agent['id']}" and edge["type"] == "recommended" for edge in graph.json()["edges"])


def test_data_source_sync_requires_admin():
    login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    response = client.post("/api/data-sources/sync", headers=headers)
    assert response.status_code == 403


def test_jd_parse():
    text = "大模型应用工程师，需要 Python、RAG、LangChain、向量数据库 和 Docker。"
    content_hash = text_hash(text)
    with SessionLocal() as db:
        existing_raw = db.scalar(select(RawJD).where(RawJD.text_hash == content_hash))
        existing_raw_id = existing_raw.id if existing_raw else None
    created_parsed_ids: list[int] = []
    raw_jd_id: int | None = existing_raw_id
    try:
        response = client.post("/api/jd/parse", json={"text": text})
        assert response.status_code == 200
        assert response.json()["job_name"] == "大模型应用工程师"
        assert response.json()["raw_jd_id"] > 0
        assert response.json()["parsed_jd_id"] > 0
        raw_jd_id = response.json()["raw_jd_id"]
        created_parsed_ids.append(response.json()["parsed_jd_id"])

        login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
        headers = {"Authorization": f"Bearer {login.json()['token']}"}
        history = client.get("/api/jd/history", headers=headers)
        assert history.status_code == 200
        assert any(item["parsed_jd_id"] == response.json()["parsed_jd_id"] for item in history.json())

        duplicate = client.post("/api/jd/parse", json={"text": text})
        assert duplicate.status_code == 200
        created_parsed_ids.append(duplicate.json()["parsed_jd_id"])
        assert duplicate.json()["deduplicated"] is True
        assert duplicate.json()["raw_jd_id"] == response.json()["raw_jd_id"]
    finally:
        with SessionLocal() as db:
            if created_parsed_ids:
                db.execute(delete(ParsedJD).where(ParsedJD.id.in_(created_parsed_ids)))
            if raw_jd_id and existing_raw_id is None:
                db.execute(delete(RawJD).where(RawJD.id == raw_jd_id))
            db.commit()


def test_admin_can_import_traceable_jd_batch_and_parse_it():
    suffix = uuid4().hex[:8]
    content = f"{suffix} 数据治理工程师，负责数据质量规则、血缘追踪和元数据管理，要求掌握 SQL、Python 与数据仓库。"
    csv_payload = (
        "title,content,external_id,source_url,published_at,publisher\n"
        f'数据治理工程师,"{content}",JOB-{suffix},https://example.com/jobs/{suffix},2026-08-01,示例发布机构\n'
        f'重复岗位,"{content}",JOB-{suffix}-DUP,https://example.com/jobs/{suffix},2026-08-01,示例发布机构\n'
        "无效岗位,太短,INVALID,https://example.com/jobs/invalid,2026-08-01,示例发布机构\n"
    ).encode("utf-8")
    source_ids: list[int] = []
    raw_ids: list[int] = []
    parsed_ids: list[int] = []
    try:
        login = client.post("/api/auth/login", json={"username": "admin_demo", "password": "Demo@123"})
        headers = {"Authorization": f"Bearer {login.json()['token']}"}
        response = client.post(
            "/api/jd/import",
            headers=headers,
            files={"file": ("jobs.csv", csv_payload, "text/csv")},
            data={
                "source_name": f"测试真实 JD 批次-{suffix}",
                "publisher": "示例发布机构",
                "source_url": "https://example.com/jobs",
                "license_name": "测试许可",
                "auto_parse": "false",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        source_ids.append(payload["id"])
        assert payload["total_count"] == 3
        assert payload["imported_count"] == 1
        assert payload["duplicate_count"] == 1
        assert payload["invalid_count"] == 1
        raw_ids.extend(item["id"] for item in payload["recent_records"])

        history = client.get("/api/jd/imports", headers=headers)
        assert history.status_code == 200
        assert history.json()[0]["id"] == payload["id"]

        parsed = client.post(f"/api/jd/imports/{payload['id']}/parse?limit=10", headers=headers)
        assert parsed.status_code == 200
        assert parsed.json()["parsed_now"] == 1
        assert parsed.json()["status"] == "parsed"
        with SessionLocal() as db:
            parsed_ids.extend(db.scalars(select(ParsedJD.id).where(ParsedJD.raw_jd_id.in_(raw_ids))).all())
    finally:
        with SessionLocal() as db:
            if parsed_ids:
                db.execute(delete(ReviewTask).where(ReviewTask.target_type == "parsed_jd", ReviewTask.target_id.in_(parsed_ids)))
                db.execute(delete(ParsedJD).where(ParsedJD.id.in_(parsed_ids)))
            if raw_ids:
                db.execute(delete(RawJD).where(RawJD.id.in_(raw_ids)))
            if source_ids:
                db.execute(delete(DataSource).where(DataSource.id.in_(source_ids)))
            db.commit()


def test_competition_catalog_has_broad_connected_coverage():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) >= 100
    assert len({job["domain"] for job in jobs}) >= 12
    assert all(job["requirements"]["skill_details"] for job in jobs)
    assert all(job["authority"]["sources"] for job in jobs)


def test_human_job_optimization_creates_skills_and_version_event():
    suffix = uuid4().hex[:8]
    job_name = f"测试岗位-{suffix}"
    skill_names = [f"测试技能A-{suffix}", f"测试技能B-{suffix}"]
    with SessionLocal() as db:
        job = JobEntity(
            name=job_name,
            domain="测试领域",
            job_type="测试类型",
            level="初级",
            description="用于验证人工优化闭环",
            is_emerging=False,
            status="active",
            version="v1.0",
            evidence="测试数据",
        )
        db.add(job)
        db.commit()
        job_id = job.id

    try:
        login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
        headers = {"Authorization": f"Bearer {login.json()['token']}"}
        response = client.put(
            f"/api/jobs/{job_id}",
            headers=headers,
            json={
                "level": "中级",
                "required_skills": [skill_names[0]],
                "preferred_skills": [skill_names[1]],
                "update_note": "根据两条真实 JD 人工复核",
                "evidence_sources": ["JD-BATCH-TEST"],
            },
        )
        assert response.status_code == 200
        assert response.json()["version"] == "v2.0"
        assert response.json()["requirements"]["required_skills"] == [skill_names[0]]

        evolution = client.get(f"/api/job-evolution/{job_id}")
        assert evolution.status_code == 200
        assert skill_names[0] in evolution.json()["added_skills"]
        assert evolution.json()["history_count"] == 1
    finally:
        with SessionLocal() as db:
            db.execute(delete(JobSkillRelation).where(JobSkillRelation.job_id == job_id))
            db.execute(delete(JobCertificateRelation).where(JobCertificateRelation.job_id == job_id))
            db.execute(delete(EvolutionEvent).where(EvolutionEvent.job_id == job_id))
            db.execute(delete(JobEntity).where(JobEntity.id == job_id))
            db.execute(delete(SkillEntity).where(SkillEntity.name.in_(skill_names)))
            db.commit()


def test_review_approval_writes_back_to_parsed_jd():
    with SessionLocal() as db:
        parsed = ParsedJD(
            raw_jd_id=None,
            job_name="待审核测试岗位",
            domain="测试领域",
            level="中级",
            responsibilities="[]",
            required_skills="[]",
            preferred_skills="[]",
            tools="[]",
            certificates="[]",
            experience="未说明",
            scenarios="[]",
            confidence=0.5,
            evidence=json.dumps({"guard_status": "needs_review"}, ensure_ascii=False),
        )
        db.add(parsed)
        db.flush()
        task = ReviewTask(
            task_type="JD解析",
            title="待审核测试岗位",
            description="测试审核写回",
            confidence=0.5,
            evidence="[]",
            status="pending",
            target_type="parsed_jd",
            target_id=parsed.id,
            payload_json="{}",
        )
        db.add(task)
        db.commit()
        parsed_id, task_id = parsed.id, task.id

    try:
        login = client.post("/api/auth/login", json={"username": "hr_admin", "password": "Demo@123"})
        headers = {"Authorization": f"Bearer {login.json()['token']}"}
        response = client.post(f"/api/review-tasks/{task_id}/approve", headers=headers)
        assert response.status_code == 200
        assert f"#{parsed_id}" in response.json()["message"]
        with SessionLocal() as db:
            parsed = db.get(ParsedJD, parsed_id)
            task = db.get(ReviewTask, task_id)
            assert json.loads(parsed.evidence)["guard_status"] == "manual_approved"
            assert task.status == "approved"
            assert task.resolved_at is not None
    finally:
        with SessionLocal() as db:
            db.execute(delete(ReviewTask).where(ReviewTask.id == task_id))
            db.execute(delete(ParsedJD).where(ParsedJD.id == parsed_id))
            db.commit()


def test_all_ai_business_routes_use_provider():
    status = client.get("/api/ai/status")
    assert status.status_code == 200
    assert {
        "jd_parse",
        "resume_parse",
        "match_analysis",
        "learning_path",
        "emerging_job_analysis",
        "digital_interview",
    }.issubset(status.json()["supported_tasks"])

    emerging = client.get("/api/emerging-jobs")
    assert emerging.status_code == 200
    assert len(emerging.json()) == 5
    assert all(item["ai_provider"] == "mock" for item in emerging.json())

    interview_login = client.post("/api/auth/login", json={"username": "student_demo", "password": "Demo@123"})
    interview_headers = {"Authorization": f"Bearer {interview_login.json()['token']}"}
    learning = client.get("/api/learning-path/999999", headers=interview_headers)
    assert learning.status_code == 404
    assert "请先完成岗位匹配分析" in learning.json()["detail"]

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
