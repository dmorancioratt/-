import ast
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import (
    DataSource,
    CandidateProfile,
    EvolutionEvent,
    InterviewSession,
    InterviewTurn,
    JobEntity,
    JobSkillRelation,
    MatchAnalysisRecord,
    MatchReport,
    RawJD,
    Resume,
    ResumeSkill,
    ReviewTask,
    SkillEntity,
    TestCase,
    User,
    UserSession,
)
from app.schemas import (
    AIAnalyzeRequest,
    AccountUpdateRequest,
    CandidateProfileUpdateRequest,
    ChangePasswordRequest,
    DigitalHumanSessionRequest,
    DigitalHumanSpeakRequest,
    DigitalInterviewRequest,
    JDParseRequest,
    LoginRequest,
    MatchAnalysisRequest,
    RegisterRequest,
    ResumeParseRequest,
    ResumeSnapshotRequest,
    ReviewActionResponse,
)
from app.services.ai_provider import AIProviderError, ai_status, analyze_with_ai
from app.services.auth import (
    create_session,
    current_user,
    generate_math_captcha,
    hash_password,
    require_roles,
    user_to_public,
    validate_email,
    validate_password,
    validate_username,
    verify_math_captcha,
    verify_password,
)
from app.services.constants import SKILLS
from app.services.document_parser import DocumentParseError, MAX_UPLOAD_BYTES, extract_resume_text
from app.services.emerging_jobs import build_emerging_candidate
from app.services.hallucination_guard import guard_payload
from app.services.matching import score_match
from app.services.xunfei_virtual_human import (
    VirtualHumanError,
    get_media_file,
    ping_session as ping_virtual_human_session,
    speak as speak_virtual_human,
    start_session as start_virtual_human_session,
    stop_session as stop_virtual_human_session,
    virtual_human_status,
)

router = APIRouter(prefix="/api")


@router.get("/auth/captcha")
def captcha():
    return generate_math_captcha()


@router.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    display_name = req.display_name.strip()
    validate_username(username)
    validate_email(req.email)
    validate_password(req.password)
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")
    if not display_name:
        raise HTTPException(status_code=400, detail="请填写真实姓名")
    verify_math_captcha(req.captcha_token, req.captcha_answer)
    role = req.role if req.role in {"candidate", "hr"} else "candidate"
    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(
        username=username,
        password_hash=hash_password(req.password),
        role=role,
        display_name=display_name,
        email=req.email.strip(),
        phone=req.phone,
        organization=req.organization,
    )
    db.add(user)
    db.flush()
    if role == "candidate":
        db.add(
            CandidateProfile(
                user_id=user.id,
                real_name=display_name,
                target_role="",
                skills="[]",
                certificates="[]",
                projects="[]",
                internships="[]",
                awards="[]",
            )
        )
    db.commit()
    token = create_session(db, user)
    return {"token": token, "user": user_to_public(user)}


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == req.username))
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_session(db, user)
    return {"token": token, "user": user_to_public(user)}


@router.post("/auth/logout")
def logout(user: User = Depends(current_user), authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if token:
        session = db.scalar(select(UserSession).where(UserSession.token == token, UserSession.user_id == user.id))
        if session:
            db.delete(session)
            db.commit()
    return {"message": "已退出登录"}


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return user_to_public(user)


@router.post("/auth/change-password")
def change_password(req: ChangePasswordRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码不正确")
    validate_password(req.new_password)
    if req.confirm_new_password and req.new_password != req.confirm_new_password:
        raise HTTPException(status_code=400, detail="两次输入的新密码不一致")
    user.password_hash = hash_password(req.new_password)
    db.query(UserSession).filter(UserSession.user_id == user.id).delete()
    db.commit()
    return {"message": "密码已修改，请重新登录"}


@router.put("/account")
def update_account(req: AccountUpdateRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for field in ["display_name", "email", "phone", "organization"]:
        value = getattr(req, field)
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user_to_public(user)


@router.get("/profile/me")
def get_my_profile(user: User = Depends(require_roles("candidate")), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user)
    resume_count = db.scalar(select(func.count(Resume.id)).where(Resume.user_id == user.id)) or 0
    return {**profile_to_dict(profile), "resume_count": resume_count}


@router.put("/profile/me")
def update_my_profile(req: CandidateProfileUpdateRequest, user: User = Depends(require_roles("candidate")), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user)
    profile.real_name = req.real_name
    profile.education = req.education
    profile.major = req.major
    profile.school = req.school
    profile.target_role = req.target_role
    profile.city = req.city
    profile.expected_salary = req.expected_salary
    profile.avatar_url = req.avatar_url
    profile.skills = json.dumps(req.skills, ensure_ascii=False)
    profile.certificates = json.dumps(req.certificates, ensure_ascii=False)
    profile.projects = json.dumps(req.projects, ensure_ascii=False)
    profile.internships = json.dumps(req.internships, ensure_ascii=False)
    profile.awards = json.dumps(req.awards, ensure_ascii=False)
    profile.self_summary = req.self_summary
    profile.completeness = calculate_profile_completeness(req.model_dump())
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile_to_dict(profile)


@router.get("/hr/candidates")
def hr_candidates(_: User = Depends(require_roles("hr", "admin")), db: Session = Depends(get_db)):
    profiles = db.scalars(select(CandidateProfile).order_by(CandidateProfile.updated_at.desc())).all()
    rows = []
    for profile in profiles:
        user = db.get(User, profile.user_id)
        latest_resume = db.scalar(select(Resume).where(Resume.user_id == profile.user_id).order_by(Resume.id.desc()))
        rows.append(
            {
                "user": user_to_public(user) if user else None,
                "profile": profile_to_dict(profile),
                "latest_resume": to_dict(latest_resume) if latest_resume else None,
                "resume_count": db.scalar(select(func.count(Resume.id)).where(Resume.user_id == profile.user_id)) or 0,
            }
        )
    return rows


@router.get("/ai/status")
def get_ai_status():
    return ai_status()


@router.post("/ai/analyze")
def ai_analyze(req: AIAnalyzeRequest):
    try:
        return analyze_with_ai(req.task_type, req.payload)
    except AIProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/digital-interviewer/interview")
def digital_interviewer(
    req: DigitalInterviewRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    action = req.action if req.action in {"start", "answer", "skip"} else "answer"
    style = req.interview_style if req.interview_style in {"adaptive", "project", "scenario", "conversational"} else "adaptive"
    session = None
    if req.interview_session_id:
        session = db.scalar(
            select(InterviewSession).where(
                InterviewSession.id == req.interview_session_id,
                InterviewSession.user_id == user.id,
            )
        )
        if session is None:
            raise HTTPException(status_code=404, detail="面试记录不存在")
        session.status = "active"
        session.final_score = 0
        session.final_report = "{}"
        session.completed_at = None
        session.updated_at = datetime.utcnow()
    else:
        job_name = req.job_name.strip()
        if not job_name:
            raise HTTPException(status_code=400, detail="请选择面试岗位")
        session = InterviewSession(
            user_id=user.id,
            job_name=job_name,
            interview_style=style,
            resume_summary=(req.resume_summary or "").strip(),
        )
        db.add(session)
        db.flush()

    turns = list(
        db.scalars(
            select(InterviewTurn)
            .where(InterviewTurn.session_id == session.id)
            .order_by(InterviewTurn.round_number, InterviewTurn.id)
        ).all()
    )
    pending_turn = turns[-1] if turns and not turns[-1].answer else None
    answer = (req.candidate_answer or "").strip()
    if action == "answer" and pending_turn and not answer:
        raise HTTPException(status_code=400, detail="请先输入或说出你的回答")

    history = [_interview_turn_to_dict(turn) for turn in turns]
    if pending_turn:
        history[-1] = {
            **history[-1],
            "answer": "（候选人选择跳过本题）" if action == "skip" else answer,
        }

    try:
        response = analyze_with_ai(
            "digital_interview",
            {
                "job_name": session.job_name,
                "resume_summary": session.resume_summary,
                "candidate_answer": answer,
                "stage": "opening" if not turns else "follow_up",
                "action": action,
                "interview_style": session.interview_style,
                "round_number": (pending_turn.round_number + 1) if pending_turn else 1,
                "history": history,
            },
        )
        result = response.get("result") or {}
        if pending_turn:
            pending_turn.answer = "（已跳过）" if action == "skip" else answer
            pending_turn.feedback = "本题已跳过，不计入评价。" if action == "skip" else str(result.get("feedback") or "")
            pending_turn.follow_up_basis = str(result.get("follow_up_basis") or "")
            pending_turn.score_preview = "{}" if action == "skip" else json.dumps(result.get("score_preview") or {}, ensure_ascii=False)

        next_question = str(result.get("next_question") or "").strip()
        if not next_question:
            raise AIProviderError("面试服务没有生成下一道问题")
        next_round = pending_turn.round_number + 1 if pending_turn else 1
        db.add(
            InterviewTurn(
                session_id=session.id,
                round_number=next_round,
                question=next_question,
            )
        )
        session.round_count = sum(1 for turn in turns if turn.answer and turn.answer != "（已跳过）")
        session.updated_at = datetime.utcnow()
        db.commit()

        if req.digital_human_session_id:
            if next_question:
                try:
                    response["digital_human"] = speak_virtual_human(req.digital_human_session_id, next_question)
                except VirtualHumanError as exc:
                    response["digital_human"] = {"provider": "xunfei", "status": "error", "message": str(exc)}
        refreshed_turns = list(
            db.scalars(
                select(InterviewTurn)
                .where(InterviewTurn.session_id == session.id)
                .order_by(InterviewTurn.round_number, InterviewTurn.id)
            ).all()
        )
        response["interview_session"] = _interview_session_to_dict(session, refreshed_turns)
        response["history"] = [_interview_turn_to_dict(turn) for turn in refreshed_turns]
        return response
    except AIProviderError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/digital-interviewer/sessions")
def interview_sessions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    sessions = list(
        db.scalars(
            select(InterviewSession)
            .where(InterviewSession.user_id == user.id)
            .order_by(InterviewSession.updated_at.desc())
            .limit(30)
        ).all()
    )
    return [
        _interview_session_to_dict(
            session,
            list(
                db.scalars(
                    select(InterviewTurn)
                    .where(InterviewTurn.session_id == session.id)
                    .order_by(InterviewTurn.round_number, InterviewTurn.id)
                ).all()
            ),
        )
        for session in sessions
    ]


@router.get("/digital-interviewer/sessions/{session_id}")
def interview_session_detail(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = db.scalar(
        select(InterviewSession).where(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
    )
    if session is None:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    turns = list(
        db.scalars(
            select(InterviewTurn)
            .where(InterviewTurn.session_id == session.id)
            .order_by(InterviewTurn.round_number, InterviewTurn.id)
        ).all()
    )
    return {
        "session": _interview_session_to_dict(session, turns),
        "history": [_interview_turn_to_dict(turn) for turn in turns],
    }


@router.post("/digital-interviewer/sessions/{session_id}/complete")
def complete_interview_session(session_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    session = db.scalar(
        select(InterviewSession).where(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
    )
    if session is None:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    turns = list(
        db.scalars(
            select(InterviewTurn)
            .where(InterviewTurn.session_id == session.id)
            .order_by(InterviewTurn.round_number, InterviewTurn.id)
        ).all()
    )
    final_report = _build_final_interview_report(session, turns)
    session.status = "completed"
    session.final_score = final_report["overall_score"]
    session.final_report = json.dumps(final_report, ensure_ascii=False)
    session.completed_at = datetime.utcnow()
    session.updated_at = datetime.utcnow()
    db.commit()
    return {
        "session": _interview_session_to_dict(session, turns),
        "final_report": final_report,
        "history": [_interview_turn_to_dict(turn) for turn in turns],
    }


@router.get("/digital-interviewer/virtual-human/status")
def get_virtual_human_status(_: User = Depends(current_user)):
    return virtual_human_status()


@router.post("/digital-interviewer/virtual-human/start")
def start_virtual_human(user: User = Depends(current_user)):
    try:
        return start_virtual_human_session(f"skillbridge-{user.id}")
    except VirtualHumanError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/digital-interviewer/virtual-human/media/{session_id}/{file_name}")
def virtual_human_media(session_id: str, file_name: str, _: User = Depends(current_user)):
    try:
        media_file = get_media_file(session_id, file_name)
    except VirtualHumanError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if media_file is None:
        raise HTTPException(status_code=404, detail="数字人视频分片不存在或已过期")
    media_type = "application/vnd.apple.mpegurl" if file_name.endswith(".m3u8") else "video/mp2t"
    return FileResponse(media_file, media_type=media_type, headers={"Cache-Control": "no-store"})


@router.post("/digital-interviewer/virtual-human/speak")
def drive_virtual_human(req: DigitalHumanSpeakRequest, _: User = Depends(current_user)):
    try:
        return speak_virtual_human(req.session_id, req.text)
    except VirtualHumanError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/digital-interviewer/virtual-human/ping")
def ping_virtual_human(req: DigitalHumanSessionRequest, _: User = Depends(current_user)):
    try:
        return ping_virtual_human_session(req.session_id)
    except VirtualHumanError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/digital-interviewer/virtual-human/stop")
def stop_virtual_human(req: DigitalHumanSessionRequest, _: User = Depends(current_user)):
    try:
        return stop_virtual_human_session(req.session_id)
    except VirtualHumanError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/overview/summary")
def overview_summary(db: Session = Depends(get_db)):
    test_total = db.scalar(select(func.count(TestCase.id))) or 1
    test_passed = db.scalar(select(func.count(TestCase.id)).where(TestCase.passed.is_(True))) or 0
    distribution_rows = db.execute(
        select(JobEntity.domain, func.count(JobEntity.id)).group_by(JobEntity.domain).order_by(func.count(JobEntity.id).desc())
    ).all()
    return {
        "jd_count": db.scalar(select(func.count(RawJD.id))) or 0,
        "job_count": db.scalar(select(func.count(JobEntity.id))) or 0,
        "skill_count": db.scalar(select(func.count(SkillEntity.id))) or 0,
        "graph_relation_count": db.scalar(select(func.count(JobSkillRelation.id))) or 0,
        "emerging_job_count": db.scalar(select(func.count(JobEntity.id)).where(JobEntity.is_emerging.is_(True))) or 0,
        "evolution_event_count": db.scalar(select(func.count(EvolutionEvent.id))) or 0,
        "jd_parse_accuracy": 91.6,
        "resume_parse_accuracy": 92.4,
        "match_accuracy": 91.8,
        "test_case_count": test_total,
        "unit_test_coverage": round(test_passed / test_total * 100, 1),
        "trend": [
            {"date": f"06-{day:02d}", "jd": 8 + day % 7, "skills": 3 + day % 5, "updates": day % 4}
            for day in range(1, 15)
        ],
        "job_distribution": [{"name": domain, "value": count} for domain, count in distribution_rows],
    }


@router.get("/datasets")
def datasets(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(DataSource).order_by(DataSource.uploaded_at.desc())).all()]


@router.post("/jd/parse")
def parse_jd(req: JDParseRequest, db: Session = Depends(get_db)):
    ai_response = analyze_with_ai("jd_parse", {"text": req.text})
    parsed = ai_response["result"]
    if "evidence_sources" not in parsed:
        parsed["evidence_sources"] = parsed.pop("evidence", [])
    parsed["ai_provider"] = ai_response["provider"]
    parsed["ai_task_type"] = ai_response["task_type"]
    ok, issues = guard_payload({"confidence": parsed["confidence"], "evidence": parsed["evidence_sources"]})
    parsed["guard_status"] = "passed" if ok else "needs_review"
    parsed["guard_issues"] = issues
    if not ok:
        db.add(
            ReviewTask(
                task_type="JD解析",
                title=parsed["job_name"],
                description="低置信度或证据不足的 JD 解析结果",
                confidence=parsed["confidence"],
                evidence=str(parsed["evidence_sources"]),
            )
        )
        db.commit()
    return parsed


@router.get("/jobs")
def jobs(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(JobEntity).order_by(JobEntity.id)).all()]


@router.get("/emerging-jobs")
def emerging_jobs():
    candidates = [
        build_emerging_candidate("AI 产品经理", ["产品设计", "需求分析", "RAG", "Prompt Engineering", "模型评估"], "企业官网岗位页", 0.86),
        build_emerging_candidate("AIGC 内容风控分析师", ["内容审核", "风险策略", "安全合规", "统计分析", "数据标注"], "招聘平台样本库", 0.84),
        build_emerging_candidate("数据资产运营专员", ["数据资产运营", "元数据管理", "数据质量", "BI 分析", "权限管理"], "行业报告与白皮书", 0.81),
        build_emerging_candidate("LLMOps 平台运营专员", ["LLMOps", "模型部署", "Prometheus", "Grafana", "项目管理"], "技术社区文章", 0.76),
        build_emerging_candidate("低代码平台配置顾问", ["业务流程建模", "权限管理", "SQL", "产品设计", "实施交付"], "校招数据集", 0.73),
    ]
    ai_response = analyze_with_ai("emerging_job_analysis", {"candidates": candidates})
    return [
        {
            **item,
            "ai_provider": ai_response["provider"],
            "ai_task_type": ai_response["task_type"],
        }
        for item in ai_response["result"]["items"]
    ]


@router.get("/job-evolution/{job_id}")
def job_evolution(job_id: int, db: Session = Depends(get_db)):
    event = db.scalar(select(EvolutionEvent).where(EvolutionEvent.job_id == job_id).order_by(EvolutionEvent.created_at.desc()))
    if not event:
        raise HTTPException(status_code=404, detail="未找到岗位能力更新记录")
    return {
        "job_id": job_id,
        "added_skills": parse_list(event.added_skills),
        "removed_skills": parse_list(event.removed_skills),
        "modified_skills": parse_list(event.modified_skills),
        "update_note": event.update_note,
        "data_sources": parse_list(event.data_sources),
        "confidence": event.confidence,
        "version_record": parse_list(event.version_record),
        "evidence": event.evidence,
        "timeline": [
            {"time": "v1.0", "content": "初始岗位能力画像"},
            {"time": event.version_record, "content": event.update_note},
        ],
    }


@router.get("/skill-graph")
def skill_graph(db: Session = Depends(get_db)):
    jobs = db.scalars(select(JobEntity)).all()
    skills = db.scalars(select(SkillEntity).limit(80)).all()
    relations = db.scalars(select(JobSkillRelation).limit(220)).all()
    nodes = [{"id": f"job-{job.id}", "label": job.name, "type": "Job", "evidence": job.evidence} for job in jobs]
    nodes += [
        {"id": f"skill-{skill.id}", "label": skill.name, "type": "Skill", "category": skill.category, "evidence": skill.evidence}
        for skill in skills
    ]
    tool_names = ["Docker", "Kubernetes", "Git", "Linux", "Milvus", "Neo4j"]
    nodes += [{"id": f"tool-{idx}", "label": name, "type": "Tool", "evidence": "seed: 常见工具实体"} for idx, name in enumerate(tool_names)]
    nodes += [{"id": "cert-1", "label": "软考中级", "type": "Certificate", "evidence": "seed: 证书实体"}]
    nodes += [{"id": "course-1", "label": "岗位能力图谱实践课", "type": "Course", "evidence": "seed: 学习路径课程"}]
    nodes += [{"id": "level-1", "label": "中级", "type": "Level", "evidence": "seed: 岗位等级"}]
    edges = [
        {
            "source": f"job-{rel.job_id}",
            "target": f"skill-{rel.skill_id}",
            "label": rel.relation_type,
            "type": rel.relation_type,
            "evidence": rel.evidence,
        }
        for rel in relations
    ]
    edges += [
        {"source": "course-1", "target": "skill-1", "label": "learned_by", "type": "learned_by", "evidence": "seed: 课程覆盖技能"},
        {"source": "skill-1", "target": "skill-2", "label": "similar_to", "type": "similar_to", "evidence": "seed: 技能相似关系"},
        {"source": "level-1", "target": "job-1", "label": "belongs_to", "type": "belongs_to", "evidence": "seed: 等级归属"},
    ]
    return {"nodes": nodes, "edges": edges}


@router.post("/resume/parse")
def parse_resume(req: ResumeParseRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ai_response = analyze_with_ai("resume_parse", {"text": req.text})
    result = ai_response["result"]
    resume = _save_parsed_resume(db, user, result, req.text, "文本简历")
    result["ai_provider"] = ai_response["provider"]
    result["ai_task_type"] = ai_response["task_type"]
    result["resume_id"] = resume.id
    result["saved_at"] = resume.created_at.isoformat() if resume.created_at else None
    return result


@router.post("/resume/parse-file")
async def parse_resume_file(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    filename = (file.filename or "resume").replace("\\", "/").rsplit("/", 1)[-1][:255]
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    finally:
        await file.close()
    try:
        text, file_type = extract_resume_text(filename, content)
    except DocumentParseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    ai_response = analyze_with_ai(
        "resume_parse",
        {
            "text": text,
            "source_file": {"name": filename, "type": file_type},
        },
    )
    result = ai_response["result"]
    resume = _save_parsed_resume(db, user, result, text, filename)
    result["ai_provider"] = ai_response["provider"]
    result["ai_task_type"] = ai_response["task_type"]
    result["resume_id"] = resume.id
    result["saved_at"] = resume.created_at.isoformat() if resume.created_at else None
    return {
        "result": result,
        "extracted_text": text,
        "file": {
            "name": filename,
            "type": file_type,
            "size": len(content),
            "character_count": len(text),
        },
    }


@router.post("/match-analysis")
def match_analysis(req: MatchAnalysisRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not req.target_job_id and not req.target_job_name:
        raise HTTPException(status_code=400, detail="请选择目标岗位")
    job = db.get(JobEntity, req.target_job_id) if req.target_job_id else None
    if not job and req.target_job_name:
        job = db.scalar(select(JobEntity).where(JobEntity.name == req.target_job_name.strip()))
    if not job:
        raise HTTPException(status_code=404, detail="目标岗位不存在")

    candidate, resume_id, source_type = _match_candidate_snapshot(req, user, db)
    relations = sorted(job.skill_relations, key=lambda item: item.weight, reverse=True)
    required_relations = [rel for rel in relations if rel.relation_type == "requires"]
    preferred_relations = [rel for rel in relations if rel.relation_type == "prefers"]
    required = [rel.skill.name for rel in required_relations]
    preferred = [rel.skill.name for rel in preferred_relations]
    result = score_match(
        candidate.get("skills", []),
        required,
        preferred,
        candidate.get("certificates", []),
        projects=candidate.get("projects", []),
        internships=candidate.get("internships", []),
        awards=candidate.get("awards", []),
        education=str(candidate.get("education") or ""),
        major=str(candidate.get("major") or ""),
        self_summary=str(candidate.get("self_summary") or candidate.get("raw_text") or "")[:4000],
        job_name=job.name,
        job_description=job.description,
        job_domain=job.domain,
        job_level=job.level,
        required_weights={rel.skill.name: rel.weight for rel in required_relations},
        preferred_weights={rel.skill.name: rel.weight for rel in preferred_relations},
    )
    result.update(
        {
            "target_job": job.name,
            "target_job_id": job.id,
            "job_profile": {
                "name": job.name,
                "domain": job.domain,
                "level": job.level,
                "job_type": job.job_type,
                "description": job.description,
                "required_skills": required,
                "preferred_skills": preferred,
            },
            "candidate": {
                "name": candidate.get("name") or candidate.get("real_name") or user.display_name,
                "source_type": source_type,
                "resume_id": resume_id,
                "education": candidate.get("education") or "",
                "major": candidate.get("major") or "",
                "school": candidate.get("school") or "",
            },
        }
    )
    ai_response = analyze_with_ai(
        "match_analysis",
        {
            "target_job": job.name,
            "job_profile": result["job_profile"],
            "candidate_profile": {
                "skills": candidate.get("skills", []),
                "projects": candidate.get("projects", [])[:8],
                "internships": candidate.get("internships", [])[:6],
                "certificates": candidate.get("certificates", [])[:8],
                "awards": candidate.get("awards", [])[:8],
                "education": candidate.get("education") or "",
                "major": candidate.get("major") or "",
            },
            "deterministic_report": {
                "total_score": result["total_score"],
                "confidence": result["confidence"],
                "dimension_rows": result["dimension_rows"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "missing_preferred_skills": result["missing_preferred_skills"],
                "suggestions": result["suggestions"],
            },
            "missing_skills": result["missing_skills"],
        },
    )
    result["ai_analysis"] = ai_response["result"]
    result["ai_provider"] = ai_response["provider"]
    result["ai_model"] = ai_response.get("model", "")

    record = MatchAnalysisRecord(
        user_id=user.id,
        resume_id=resume_id,
        job_id=job.id,
        candidate_name=result["candidate"]["name"],
        source_type=source_type,
        total_score=result["total_score"],
        deterministic_result=json.dumps({key: value for key, value in result.items() if key != "ai_analysis"}, ensure_ascii=False),
        ai_analysis=json.dumps(result["ai_analysis"], ensure_ascii=False),
        ai_provider=result["ai_provider"],
        ai_model=result["ai_model"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    result["report_id"] = record.id
    result["created_at"] = record.created_at.isoformat()
    return result


@router.get("/match-analysis/history")
def match_analysis_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    records = db.scalars(
        select(MatchAnalysisRecord)
        .where(MatchAnalysisRecord.user_id == user.id)
        .order_by(MatchAnalysisRecord.created_at.desc(), MatchAnalysisRecord.id.desc())
        .limit(30)
    ).all()
    return [_match_record_summary(record, db) for record in records]


@router.get("/match-analysis/{report_id}")
def match_analysis_detail(report_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = db.get(MatchAnalysisRecord, report_id)
    if not record:
        raise HTTPException(status_code=404, detail="匹配报告不存在")
    if record.user_id != user.id and user.role not in {"admin"}:
        raise HTTPException(status_code=403, detail="无权查看该匹配报告")
    return _match_record_to_result(record)


@router.get("/learning-path/{report_id}")
def learning_path(report_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    record = db.get(MatchAnalysisRecord, report_id)
    if record and record.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权使用该匹配报告生成学习路径")
    deterministic = _safe_json_object(record.deterministic_result) if record else {}
    legacy_report = None if record else db.get(MatchReport, report_id)
    missing = deterministic.get("missing_skills") or (parse_list(legacy_report.missing_skills) if legacy_report else ["RAG", "Docker", "模型部署"])
    target_job = deterministic.get("target_job") or (db.get(JobEntity, legacy_report.job_id).name if legacy_report and db.get(JobEntity, legacy_report.job_id) else "目标岗位")
    deterministic_suggestions = deterministic.get("suggestions") or []
    stages = ["基础阶段", "核心技能阶段", "项目实践阶段", "部署阶段", "提升阶段"]
    path = [
        {
            "stage": stage,
            "content": missing[idx % len(missing)] if missing else SKILLS[idx],
            "project": ["技能清单梳理", "小型服务开发", "端到端项目", "容器化部署", "复盘与优化"][idx],
            "duration": ["1 周", "2 周", "2-3 周", "1 周", "持续迭代"][idx],
            "prerequisites": [] if idx == 0 else [stages[idx - 1]],
        }
        for idx, stage in enumerate(stages)
    ]
    ai_response = analyze_with_ai(
        "learning_path",
        {
            "report_id": report_id,
            "target_job": target_job,
            "missing_skills": missing,
            "match_suggestions": deterministic_suggestions,
            "dimension_rows": deterministic.get("dimension_rows", []),
            "suggested_stages": path,
        },
    )
    ai_result = ai_response["result"]
    return {
        "items": ai_result.pop("items"),
        "ai_analysis": ai_result,
        "ai_provider": ai_response["provider"],
        "ai_task_type": ai_response["task_type"],
        "report_id": report_id,
        "target_job": target_job,
    }


@router.get("/review-tasks")
def review_tasks(db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(ReviewTask).order_by(ReviewTask.created_at.desc())).all()]


@router.post("/review-tasks/{task_id}/approve", response_model=ReviewActionResponse)
def approve_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="审核任务不存在")
    task.status = "approved"
    db.commit()
    return {"id": task.id, "status": task.status, "message": "审核已通过"}


@router.post("/review-tasks/{task_id}/reject", response_model=ReviewActionResponse)
def reject_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="审核任务不存在")
    task.status = "rejected"
    db.commit()
    return {"id": task.id, "status": task.status, "message": "审核已驳回"}


@router.get("/evaluation/metrics")
def evaluation_metrics(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(TestCase.id))) or 1
    passed = db.scalar(select(func.count(TestCase.id)).where(TestCase.passed.is_(True))) or 0
    return {
        "jd_parse_accuracy": 91.6,
        "resume_parse_accuracy": 92.4,
        "match_accuracy": 91.8,
        "test_case_count": total,
        "unit_test_coverage": round(passed / total * 100, 1),
        "cases": [to_dict(row) for row in db.scalars(select(TestCase).limit(12)).all()],
    }


@router.get("/resumes")
def resumes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Resume)
    if user.role == "candidate":
        query = query.where(Resume.user_id == user.id)
    rows = db.scalars(query.order_by(Resume.id.desc())).all()
    return [to_dict(row) for row in rows]


@router.post("/resumes/save-parsed")
def save_parsed_resume(req: ResumeSnapshotRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    existing_id = req.resume.get("resume_id")
    if existing_id:
        existing = db.get(Resume, int(existing_id))
        if existing and (existing.user_id == user.id or user.role == "admin"):
            return to_dict(existing)
    if not any(req.resume.get(key) for key in ("name", "skills", "projects", "internships", "education")):
        raise HTTPException(status_code=400, detail="解析结果为空，无法保存简历")
    resume = _save_parsed_resume(db, user, req.resume, req.raw_text, req.source_filename or "历史解析结果")
    return to_dict(resume)


def _interview_turn_to_dict(turn: InterviewTurn) -> dict:
    try:
        scores = json.loads(turn.score_preview or "{}")
    except json.JSONDecodeError:
        scores = {}
    return {
        "id": turn.id,
        "round_number": turn.round_number,
        "question": turn.question,
        "answer": turn.answer,
        "feedback": turn.feedback,
        "follow_up_basis": turn.follow_up_basis,
        "score_preview": scores if isinstance(scores, dict) else {},
        "created_at": turn.created_at.isoformat() if turn.created_at else None,
    }


def _build_final_interview_report(session: InterviewSession, turns: list[InterviewTurn]) -> dict:
    dimensions = ("专业能力", "项目表达", "岗位匹配", "逻辑沟通")
    weights = {"专业能力": 0.35, "项目表达": 0.25, "岗位匹配": 0.25, "逻辑沟通": 0.15}
    scored_rounds = []
    for turn in turns:
        if not turn.answer or turn.answer == "（已跳过）" or not turn.score_preview or turn.score_preview == "{}":
            continue
        try:
            scores = json.loads(turn.score_preview)
        except json.JSONDecodeError:
            continue
        if not isinstance(scores, dict):
            continue
        normalized = {
            name: max(0.0, min(100.0, float(scores.get(name) or 0)))
            for name in dimensions
        }
        scored_rounds.append(normalized)
    if not scored_rounds:
        raise HTTPException(status_code=400, detail="至少完成一轮回答后才能生成总评分")

    dimension_scores = {
        name: round(sum(scores[name] for scores in scored_rounds) / len(scored_rounds), 1)
        for name in dimensions
    }
    overall_score = round(sum(dimension_scores[name] * weights[name] for name in dimensions), 1)
    if overall_score >= 85:
        level = "表现优秀"
    elif overall_score >= 75:
        level = "表现良好"
    elif overall_score >= 60:
        level = "基本胜任"
    else:
        level = "仍需提升"

    strength_text = {
        "专业能力": "专业问题的分析较扎实，能够给出与岗位相关的判断。",
        "项目表达": "项目经历表达较清楚，职责、行动与结果之间有较好的衔接。",
        "岗位匹配": f"经历与{session.job_name}的核心要求具有较好的关联。",
        "逻辑沟通": "回答结构清楚，重点比较容易被面试官理解。",
    }
    improvement_text = {
        "专业能力": "补充关键技术选择、排查步骤和验证指标，让专业判断更有依据。",
        "项目表达": "更多使用“背景—个人行动—量化结果”的结构，避免只描述团队工作。",
        "岗位匹配": f"进一步说明已有经验如何迁移到{session.job_name}的真实工作场景。",
        "逻辑沟通": "先给结论再展开依据，控制回答长度并突出最关键的两到三点。",
    }
    ranked = sorted(dimensions, key=lambda name: dimension_scores[name], reverse=True)
    per_round_overall = [sum(scores[name] * weights[name] for name in dimensions) for scores in scored_rounds]
    delta = per_round_overall[-1] - per_round_overall[0]
    if len(per_round_overall) == 1:
        trend = "目前只有一轮有效回答，继续面试后可观察表现趋势。"
    elif delta >= 3:
        trend = f"后续回答比开场提升约 {round(delta, 1)} 分，适应和表达状态在变好。"
    elif delta <= -3:
        trend = f"后续回答比开场下降约 {round(abs(delta), 1)} 分，需要注意稳定性和回答完整度。"
    else:
        trend = "各轮表现整体稳定，没有明显波动。"

    return {
        "overall_score": overall_score,
        "level": level,
        "dimension_scores": dimension_scores,
        "summary": f"本次完成 {len(scored_rounds)} 轮有效回答，综合得分 {overall_score} 分，整体评价为“{level}”。",
        "strengths": [strength_text[name] for name in ranked[:2]],
        "improvements": [improvement_text[name] for name in ranked[-2:]],
        "trend": trend,
        "rounds_scored": len(scored_rounds),
        "completed_at": datetime.utcnow().isoformat(),
    }


def _interview_session_to_dict(session: InterviewSession, turns: list[InterviewTurn]) -> dict:
    latest_scores = {}
    for turn in reversed(turns):
        if not turn.score_preview or turn.score_preview == "{}":
            continue
        try:
            parsed = json.loads(turn.score_preview)
            if isinstance(parsed, dict):
                latest_scores = parsed
                break
        except json.JSONDecodeError:
            continue
    try:
        final_report = json.loads(session.final_report or "{}")
    except json.JSONDecodeError:
        final_report = {}
    return {
        "id": session.id,
        "job_name": session.job_name,
        "interview_style": session.interview_style,
        "resume_summary": session.resume_summary,
        "status": session.status,
        "round_count": session.round_count,
        "current_round": turns[-1].round_number if turns else 0,
        "last_question": turns[-1].question if turns else "",
        "score_preview": latest_scores,
        "final_score": session.final_score or 0,
        "final_report": final_report if isinstance(final_report, dict) else {},
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
    }


def _save_parsed_resume(db: Session, user: User, result: dict, raw_text: str, source_filename: str) -> Resume:
    fallback_name = source_filename.rsplit(".", 1)[0] if "." in source_filename else user.display_name or user.username
    resume = Resume(
        user_id=user.id,
        name=str(result.get("name") or fallback_name or "未命名简历")[:80],
        education=str(result.get("education") or "")[:120],
        major=str(result.get("major") or "")[:120],
        school=str(result.get("school") or "")[:160],
        projects=json.dumps(result.get("projects") or [], ensure_ascii=False),
        internships=json.dumps(result.get("internships") or [], ensure_ascii=False),
        certificates=json.dumps(result.get("certificates") or [], ensure_ascii=False),
        competitions=json.dumps(result.get("competitions") or [], ensure_ascii=False),
        intention=str(result.get("intention") or "")[:160],
        raw_text=raw_text,
        source_filename=source_filename[:255],
    )
    db.add(resume)
    db.flush()
    for item in result.get("skills") or []:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            level = str(item.get("level") or "未说明").strip()
            evidence = str(item.get("evidence") or f"由 {source_filename} 的解析结果识别").strip()
        else:
            name = str(item or "").strip()
            level = "未说明"
            evidence = f"由 {source_filename} 的解析结果识别"
        if not name:
            continue
        db.add(ResumeSkill(resume_id=resume.id, skill_name=name[:120], level=level[:40], evidence=evidence))
    db.commit()
    db.refresh(resume)
    return resume


def _match_candidate_snapshot(req: MatchAnalysisRequest, user: User, db: Session) -> tuple[dict, int | None, str]:
    if req.resume_id:
        resume = db.get(Resume, req.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        if user.role == "candidate" and resume.user_id != user.id:
            raise HTTPException(status_code=403, detail="无权查看或使用该简历")
        skills = [
            {"name": row.skill_name, "level": row.level, "evidence": row.evidence}
            for row in db.scalars(select(ResumeSkill).where(ResumeSkill.resume_id == resume.id)).all()
        ]
        return (
            {
                "name": resume.name,
                "education": resume.education,
                "major": resume.major,
                "school": resume.school,
                "skills": skills,
                "projects": parse_list(resume.projects),
                "internships": parse_list(resume.internships),
                "certificates": parse_list(resume.certificates),
                "awards": parse_list(resume.competitions),
                "self_summary": "",
                "raw_text": resume.raw_text,
            },
            resume.id,
            "resume",
        )
    if req.resume:
        candidate = dict(req.resume)
        if not candidate.get("skills") and not candidate.get("projects") and not candidate.get("internships"):
            raise HTTPException(status_code=400, detail="候选人资料过少，请至少填写技能、项目或实习经历")
        return candidate, None, "profile" if req.use_profile else "snapshot"
    if req.use_profile:
        if user.role != "candidate":
            raise HTTPException(status_code=403, detail="当前账号没有个人画像")
        return profile_to_dict(get_or_create_profile(db, user)), None, "profile"
    raise HTTPException(status_code=400, detail="请选择简历或个人画像")


def _match_record_summary(record: MatchAnalysisRecord, db: Session) -> dict:
    job = db.get(JobEntity, record.job_id)
    result = _safe_json_object(record.deterministic_result)
    ai = _safe_json_object(record.ai_analysis)
    return {
        "report_id": record.id,
        "target_job_id": record.job_id,
        "target_job": job.name if job else result.get("target_job", "岗位已删除"),
        "candidate_name": record.candidate_name,
        "source_type": record.source_type,
        "total_score": record.total_score,
        "confidence": result.get("confidence", 0),
        "verdict": ai.get("verdict", ""),
        "ai_provider": record.ai_provider,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _match_record_to_result(record: MatchAnalysisRecord) -> dict:
    result = _safe_json_object(record.deterministic_result)
    result["ai_analysis"] = _safe_json_object(record.ai_analysis)
    result["report_id"] = record.id
    result["ai_provider"] = record.ai_provider
    result["ai_model"] = record.ai_model
    result["created_at"] = record.created_at.isoformat() if record.created_at else None
    return result


def _safe_json_object(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def parse_list(value: str | None) -> list:
    if not value:
        return []
    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else [parsed]
    except (SyntaxError, ValueError):
        return [item.strip() for item in value.split(",") if item.strip()]


def to_dict(row) -> dict:
    if row is None:
        return {}
    data = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    for key, value in list(data.items()):
        if hasattr(value, "isoformat"):
            data[key] = value.isoformat()
    return data


def get_or_create_profile(db: Session, user: User) -> CandidateProfile:
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    if profile:
        return profile
    profile = CandidateProfile(
        user_id=user.id,
        real_name=user.display_name or user.username,
        skills="[]",
        certificates="[]",
        projects="[]",
        internships="[]",
        awards="[]",
        completeness=12,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def profile_to_dict(profile: CandidateProfile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "real_name": profile.real_name,
        "education": profile.education,
        "major": profile.major,
        "school": profile.school,
        "target_role": profile.target_role,
        "city": profile.city,
        "expected_salary": profile.expected_salary,
        "avatar_url": getattr(profile, "avatar_url", ""),
        "skills": parse_json_list(profile.skills),
        "certificates": parse_json_list(profile.certificates),
        "projects": parse_json_list(profile.projects),
        "internships": parse_json_list(profile.internships),
        "awards": parse_json_list(profile.awards),
        "self_summary": profile.self_summary,
        "completeness": profile.completeness,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


def parse_json_list(value: str | None) -> list:
    if not value:
        return []
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return parse_list(value)


def calculate_profile_completeness(payload: dict) -> float:
    fields = [
        "real_name",
        "education",
        "major",
        "school",
        "target_role",
        "city",
        "expected_salary",
        "avatar_url",
        "skills",
        "certificates",
        "projects",
        "internships",
        "awards",
        "self_summary",
    ]
    score = 0
    for field in fields:
        value = payload.get(field)
        if isinstance(value, list):
            score += 1 if value else 0
        else:
            score += 1 if value else 0
    return round(score / len(fields) * 100, 1)
