import ast
import csv
import io
import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import (
    CertificateEntity,
    DataSource,
    CandidateProfile,
    EvolutionEvent,
    ExternalCatalogItem,
    InterviewSession,
    InterviewTurn,
    JobEntity,
    JobCertificateRelation,
    JobSkillRelation,
    LearningResourceProgress,
    LearningTask,
    MatchAnalysisRecord,
    MatchReport,
    ParsedJD,
    RawJD,
    Resume,
    ResumeSkill,
    ReviewTask,
    SystemSetting,
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
    GovernanceSettingsRequest,
    LearningProgressRequest,
    LearningTaskUpdateRequest,
    JobUpdateRequest,
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
from app.services.capability_catalog import enriched_job, job_authority, job_requirements, resolve_onet
from app.services.emerging_jobs import build_emerging_candidate
from app.services.hallucination_guard import guard_payload, get_governance_rules
from app.services.jd_parser import text_hash
from app.services.jd_integration import publish_jd_batch
from app.services.matching import score_match
from app.services.official_data import catalog_to_dict, market_snapshot, source_to_dict, sync_official_data, sync_status
from app.services.source_trust import source_validation_report, validate_source_trust
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

INTERVIEW_SCORE_FLOOR = 0.0
INTERVIEW_SCORE_CEILING = 95.0
INTERVIEW_TARGET_SCORED_ROUNDS = 6
INTERVIEW_MIN_REPORT_ROUNDS = 3
INTERVIEW_MAX_TOTAL_TURNS = 8
INTERVIEW_DIMENSIONS = ("专业能力", "项目表达", "岗位匹配", "逻辑沟通")

INTERVIEW_FOCUS_PLAN = {
    "adaptive": ["项目经历", "技术深度", "问题排查", "业务理解", "协作沟通", "成长复盘"],
    "project": ["项目背景", "个人职责", "关键难点", "技术取舍", "量化结果", "复盘改进"],
    "scenario": ["任务拆解", "风险识别", "资源协调", "异常处理", "结果验证", "复盘改进"],
    "conversational": ["动机匹配", "经历亮点", "困难处理", "协作方式", "学习能力", "未来规划"],
}

INTERVIEW_FALLBACK_QUESTIONS = {
    "项目经历": "请介绍一个最能代表你能力的项目，重点说清楚目标、你的职责和最终结果。",
    "技术深度": "在刚才的经历里，哪个技术选择最关键？你当时为什么这样选，有没有替代方案？",
    "问题排查": "如果这个项目在线上出现异常，你会按什么顺序定位问题，并如何判断修复是否有效？",
    "业务理解": "这个项目解决了什么真实业务问题？你怎么衡量它不是只完成了功能，而是产生了价值？",
    "协作沟通": "当团队成员对方案有不同意见时，你通常怎么推动形成结论？请结合一次真实经历说明。",
    "成长复盘": "如果让你重新做一次这段经历，你最想改进哪一个决定？为什么？",
    "项目背景": "请先讲清楚一个你投入最多的项目：背景是什么、目标是什么、你承担了哪部分？",
    "个人职责": "这个项目里哪些工作是你独立负责的？请区分团队成果和你的个人贡献。",
    "关键难点": "项目推进中最难的一步是什么？你遇到的约束、尝试过的方法和最终处理结果分别是什么？",
    "技术取舍": "你在这个项目里做过哪次重要技术取舍？请说明判断标准和代价。",
    "量化结果": "这个项目最后如何验收？有没有数据、用户反馈或业务指标能说明效果？",
    "任务拆解": "面对一个目标不清、资料不完整的任务，你会如何拆出第一周的行动计划？",
    "风险识别": "如果任务进入执行期后发现关键假设不成立，你会如何评估影响并调整方案？",
    "资源协调": "当资源不足、时间又很紧时，你会如何排优先级并和相关方同步预期？",
    "异常处理": "请描述一次计划外问题出现时你的处理方式：你先确认什么，再推动什么？",
    "结果验证": "完成方案后，你会用哪些证据判断它真正有效，而不是只是看起来完成了？",
    "动机匹配": "你为什么想做这个岗位？哪段经历最能说明这个选择不是一时兴趣？",
    "经历亮点": "请讲一段你最有成就感的经历，重点说清楚你做对了什么。",
    "困难处理": "你遇到过最棘手的学习或项目困难是什么？你怎么走出来的？",
    "协作方式": "你习惯怎样和同学、同事或业务方协作？请用一次具体经历说明。",
    "学习能力": "最近半年你主动学习过哪项能力？你怎么验证自己已经能用起来？",
    "未来规划": "如果进入这个岗位，你希望前三个月补齐哪两项能力？计划怎么做？",
}


def _coverage_summary() -> dict:
    report_path = Path(__file__).resolve().parents[1] / "evaluation" / "reports" / "coverage_summary.json"
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        return {
            "coverage": float(payload.get("coverage") or 0),
            "generated_at": payload.get("generated_at"),
            "command": payload.get("command") or "python -m app.evaluation.run_coverage",
            "note": f"标准库逐行追踪：{payload.get('covered_lines', 0)}/{payload.get('executable_lines', 0)} 行。",
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {
            "coverage": None,
            "generated_at": None,
            "command": "python -m app.evaluation.run_coverage",
            "note": "尚未生成覆盖率报告，请先运行可复现覆盖率命令。",
        }


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
        if session.status == "completed":
            raise HTTPException(status_code=400, detail="这场面试已经结束，请新建一场面试")
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
    answered_before = _scored_round_count(turns)
    if action == "skip" and pending_turn and len(turns) >= INTERVIEW_MAX_TOTAL_TURNS and answered_before < INTERVIEW_MIN_REPORT_ROUNDS:
        raise HTTPException(status_code=400, detail=f"本场跳题过多，请至少完成 {INTERVIEW_MIN_REPORT_ROUNDS} 轮有效回答后再生成总评")
    next_focus = _next_interview_focus(session.interview_style, answered_before)

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
                "asked_questions": [turn.question for turn in turns],
                "covered_focus": _covered_interview_focus(session.interview_style, answered_before),
                "next_focus": next_focus,
                "target_scored_rounds": INTERVIEW_TARGET_SCORED_ROUNDS,
                "remaining_scored_rounds": max(0, INTERVIEW_TARGET_SCORED_ROUNDS - answered_before),
            },
        )
        result = response.get("result") or {}
        if pending_turn:
            pending_turn.answer = "（已跳过）" if action == "skip" else answer
            pending_turn.feedback = "本题已跳过，不计入评价。" if action == "skip" else str(result.get("feedback") or "")
            pending_turn.follow_up_basis = str(result.get("follow_up_basis") or "")
            scores = _bounded_interview_scores(result.get("score_preview") or {}, answer)
            pending_turn.score_preview = "{}" if action == "skip" else json.dumps(scores, ensure_ascii=False)

        session.round_count = _scored_round_count(turns)
        should_complete = (
            session.round_count >= INTERVIEW_TARGET_SCORED_ROUNDS
            or (len(turns) >= INTERVIEW_MAX_TOTAL_TURNS and session.round_count >= INTERVIEW_MIN_REPORT_ROUNDS)
        )
        if should_complete:
            final_report = _build_final_interview_report(session, turns)
            session.status = "completed"
            session.final_score = final_report["overall_score"]
            session.final_report = json.dumps(final_report, ensure_ascii=False)
            session.completed_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            db.commit()
            refreshed_turns = list(
                db.scalars(
                    select(InterviewTurn)
                    .where(InterviewTurn.session_id == session.id)
                    .order_by(InterviewTurn.round_number, InterviewTurn.id)
                ).all()
            )
            response["result"] = {
                **result,
                "next_question": "",
                "follow_up_basis": "已达到本场面试的有效回答轮次，自动生成总评。",
                "feedback": result.get("feedback") or "本轮回答已记录，面试自动结束。",
            }
            response["auto_completed"] = True
            response["final_report"] = final_report
            response["interview_session"] = _interview_session_to_dict(session, refreshed_turns)
            response["history"] = [_interview_turn_to_dict(turn) for turn in refreshed_turns]
            return response

        next_question = str(result.get("next_question") or "").strip()
        if not next_question:
            raise AIProviderError("面试服务没有生成下一道问题")
        next_question = _deduplicate_interview_question(
            next_question,
            [turn.question for turn in turns],
            session.interview_style,
            next_focus,
        )
        next_round = pending_turn.round_number + 1 if pending_turn else 1
        db.add(
            InterviewTurn(
                session_id=session.id,
                round_number=next_round,
                question=next_question,
            )
        )
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
    from app.evaluation.generate_match_predictions import generate as generate_match_predictions
    from app.evaluation.run_eval import SAMPLES_DIR, eval_match, eval_skill_extraction

    test_total = db.scalar(select(func.count(TestCase.id))) or 1
    test_passed = db.scalar(select(func.count(TestCase.id)).where(TestCase.passed.is_(True))) or 0
    distribution_rows = db.execute(
        select(JobEntity.domain, func.count(JobEntity.id)).group_by(JobEntity.domain).order_by(func.count(JobEntity.id).desc())
    ).all()
    generate_match_predictions()
    gold = SAMPLES_DIR / "gold"
    pred = SAMPLES_DIR / "pred"
    evaluation_items = [
        eval_skill_extraction("jd_extraction", "JD 技能抽取", gold / "jd_gold.jsonl", pred / "jd_pred.jsonl"),
        eval_skill_extraction("resume_extraction", "简历技能抽取", gold / "resume_gold.jsonl", pred / "resume_pred.jsonl"),
        eval_match(gold / "match_gold.jsonl", pred / "match_pred.jsonl"),
    ]
    evaluation = {item.task: item for item in evaluation_items}
    coverage = _coverage_summary()
    market = market_snapshot(db)
    skill_relation_count = db.scalar(select(func.count(JobSkillRelation.id))) or 0
    certificate_relation_count = db.scalar(select(func.count(JobCertificateRelation.id))) or 0
    return {
        "jd_count": db.scalar(select(func.count(RawJD.id))) or 0,
        "parsed_jd_count": db.scalar(select(func.count(ParsedJD.id))) or 0,
        "resume_count": db.scalar(select(func.count(Resume.id))) or 0,
        "job_count": db.scalar(select(func.count(JobEntity.id))) or 0,
        "skill_count": db.scalar(select(func.count(SkillEntity.id))) or 0,
        "graph_relation_count": skill_relation_count + certificate_relation_count,
        "skill_relation_count": skill_relation_count,
        "certificate_count": db.scalar(select(func.count(CertificateEntity.id))) or 0,
        "certificate_relation_count": certificate_relation_count,
        "emerging_job_count": db.scalar(select(func.count(JobEntity.id)).where(JobEntity.is_emerging.is_(True))) or 0,
        "evolution_event_count": db.scalar(select(func.count(EvolutionEvent.id))) or 0,
        "jd_parse_accuracy": round((evaluation["jd_extraction"].f1 or 0) * 100, 2),
        "resume_parse_accuracy": round((evaluation["resume_extraction"].f1 or 0) * 100, 2),
        "match_accuracy": round((evaluation["job_match"].accuracy or 0) * 100, 2),
        "benchmark_sample_count": sum(item.samples for item in evaluation.values()),
        "test_case_count": test_total,
        "business_case_pass_rate": round(test_passed / test_total * 100, 1),
        "unit_test_coverage": coverage["coverage"],
        "unit_test_coverage_generated_at": coverage["generated_at"],
        "trend": [
            {
                "date": item["period"],
                "value": item["value"],
                "unit": item["unit"],
                "source": "工业和信息化部",
                "evidence_url": item["evidence_url"],
            }
            for item in market["software_revenue_trend"]
        ],
        "job_distribution": [{"name": domain, "value": count} for domain, count in distribution_rows],
        "market_coverage": market["coverage"],
        "market_as_of": market["as_of"],
        "market_last_synced_at": market["last_synced_at"],
    }


def _guard_stats(db: Session) -> dict:
    """基于 ParsedJD 的置信度与证据链，统计幻觉防护结果（取样最近 1000 条）。"""
    total_in_db = db.scalar(select(func.count(ParsedJD.id))) or 0
    rows = db.execute(
        select(ParsedJD.id, ParsedJD.job_name, ParsedJD.confidence, ParsedJD.evidence)
        .order_by(ParsedJD.id.desc())
        .limit(1000)
    ).all()
    flagged = []
    rule_hits = {"missing_evidence": 0, "low_confidence": 0}
    rules = get_governance_rules(db)
    for row in rows:
        try:
            evidence = json.loads(row.evidence or "{}")
        except (json.JSONDecodeError, TypeError):
            evidence = {}
        issues = evidence.get("guard_issues")
        if issues is None:
            ok, issues = guard_payload({"confidence": row.confidence, "evidence": evidence.get("evidence_sources")}, rules)
            if ok:
                issues = []
        if "缺少 evidence 字段" in issues:
            rule_hits["missing_evidence"] += 1
        if "置信度低于阈值" in issues:
            rule_hits["low_confidence"] += 1
        if issues:
            flagged.append({
                "id": row.id,
                "job_name": row.job_name,
                "confidence": round(float(row.confidence or 0), 4),
                "issues": issues,
                "guard_status": evidence.get("guard_status", "needs_review"),
            })
    sample = len(rows)
    passed = sample - len(flagged)
    return {
        "total_checked": total_in_db,
        "sample_size": sample,
        "passed": passed,
        "flagged": len(flagged),
        "pass_rate": round(passed / sample * 100, 1) if sample else 0,
        "min_confidence": rules.confidence_threshold,
        "rules": [
            {"key": "low_confidence", "label": "置信度阈值检测", "detail": f"解析结果置信度低于 {rules.confidence_threshold} 时标记待复核", "hits": rule_hits["low_confidence"]},
            {"key": "missing_evidence", "label": "证据链缺失检测", "detail": "结构化输出缺少 evidence 字段时拒绝直接发布", "hits": rule_hits["missing_evidence"]},
        ],
        "recent_events": flagged[:6],
        "pipeline_stage": "AI 结构化解析 → 幻觉防护 → 低置信结果转人工复核",
    }


@router.get("/governance/hallucination")
def governance_hallucination(db: Session = Depends(get_db)):
    return _guard_stats(db)


def _settings_payload(row: SystemSetting) -> dict:
    return {
        "evidence_required": bool(row.evidence_required),
        "low_confidence_review": bool(row.low_confidence_review),
        "version_history": bool(row.version_history),
        "confidence_threshold": float(row.confidence_threshold),
        "updated_by": row.updated_by,
        "updated_at": row.updated_at,
    }


@router.get("/settings/governance")
def governance_settings(
    _: User = Depends(require_roles("admin", "hr")),
    db: Session = Depends(get_db),
):
    get_governance_rules(db)
    db.commit()
    return _settings_payload(db.get(SystemSetting, 1))


@router.put("/settings/governance")
def update_governance_settings(
    req: GovernanceSettingsRequest,
    user: User = Depends(require_roles("admin", "hr")),
    db: Session = Depends(get_db),
):
    row = db.get(SystemSetting, 1) or SystemSetting(id=1)
    row.evidence_required = req.evidence_required
    row.low_confidence_review = req.low_confidence_review
    row.version_history = req.version_history
    row.confidence_threshold = req.confidence_threshold
    row.updated_by = user.id
    row.updated_at = datetime.utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return _settings_payload(row)


@router.get("/system/metrics")
def system_metrics(_: User = Depends(require_roles("admin"))):
    """Read live host metrics; values are sampled from the running backend host."""
    try:
        import psutil
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="后端缺少 psutil，无法读取真实系统指标") from exc
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path(__file__).resolve().anchor))
    network = psutil.net_io_counters()
    process = psutil.Process(os.getpid())
    return {
        "sampled_at": datetime.utcnow(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "cpu_count": psutil.cpu_count(logical=True) or 0,
        "memory_percent": memory.percent,
        "memory_used_bytes": memory.used,
        "memory_total_bytes": memory.total,
        "disk_percent": disk.percent,
        "disk_used_bytes": disk.used,
        "disk_total_bytes": disk.total,
        "network_sent_bytes": network.bytes_sent,
        "network_received_bytes": network.bytes_recv,
        "process_memory_bytes": process.memory_info().rss,
        "process_uptime_seconds": max(0, int(datetime.utcnow().timestamp() - process.create_time())),
    }


def _latest_learning_report(db: Session, user_id: int) -> MatchAnalysisRecord | None:
    return db.scalar(
        select(MatchAnalysisRecord)
        .where(MatchAnalysisRecord.user_id == user_id)
        .order_by(MatchAnalysisRecord.created_at.desc(), MatchAnalysisRecord.id.desc())
    )


def _report_learning_inputs(report: MatchAnalysisRecord) -> tuple[list[str], list[str]]:
    try:
        deterministic = json.loads(report.deterministic_result or "{}")
    except (json.JSONDecodeError, TypeError):
        deterministic = {}
    try:
        ai = json.loads(report.ai_analysis or "{}")
    except (json.JSONDecodeError, TypeError):
        ai = {}
    skills = [str(item).strip() for item in deterministic.get("missing_skills", []) if str(item).strip()]
    suggestions = [str(item).strip() for item in ai.get("suggestions", []) if str(item).strip()]
    if not suggestions:
        suggestions = [str(item).strip() for item in deterministic.get("suggestions", []) if str(item).strip()]
    return list(dict.fromkeys(skills)), list(dict.fromkeys(suggestions))


def _sync_learning_records(db: Session, user_id: int) -> None:
    report = _latest_learning_report(db, user_id)
    if report is None:
        return
    skills, suggestions = _report_learning_inputs(report)
    for index, skill in enumerate(skills[:8]):
        title = f"完成 {skill} 能力补强"
        existing_task = db.scalar(select(LearningTask).where(
            LearningTask.user_id == user_id,
            LearningTask.source_report_id == report.id,
            LearningTask.title == title,
        ))
        if existing_task is None:
            db.add(LearningTask(
                user_id=user_id,
                source_report_id=report.id,
                title=title,
                description=suggestions[index] if index < len(suggestions) else f"根据最近岗位匹配报告补齐 {skill} 能力证据。",
            ))
        existing_resource = db.scalar(select(LearningResourceProgress).where(
            LearningResourceProgress.user_id == user_id,
            LearningResourceProgress.source_report_id == report.id,
            LearningResourceProgress.skill_name == skill,
        ))
        if existing_resource is None:
            db.add(LearningResourceProgress(
                user_id=user_id,
                source_report_id=report.id,
                skill_name=skill,
                title=f"{skill} 专题学习与项目实践",
            ))
    db.commit()


@router.get("/learning/tasks")
def learning_tasks(user: User = Depends(require_roles("candidate")), db: Session = Depends(get_db)):
    _sync_learning_records(db, user.id)
    rows = db.scalars(select(LearningTask).where(LearningTask.user_id == user.id).order_by(LearningTask.created_at.desc())).all()
    return [to_dict(row) for row in rows]


@router.put("/learning/tasks/{task_id}")
def update_learning_task(
    task_id: int,
    req: LearningTaskUpdateRequest,
    user: User = Depends(require_roles("candidate")),
    db: Session = Depends(get_db),
):
    if req.status not in {"pending", "completed"}:
        raise HTTPException(status_code=400, detail="任务状态仅支持 pending 或 completed")
    row = db.get(LearningTask, task_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="学习任务不存在")
    row.status = req.status
    row.completed_at = datetime.utcnow() if req.status == "completed" else None
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return to_dict(row)


@router.get("/learning/resources")
def learning_resources(user: User = Depends(require_roles("candidate")), db: Session = Depends(get_db)):
    _sync_learning_records(db, user.id)
    rows = db.scalars(select(LearningResourceProgress).where(
        LearningResourceProgress.user_id == user.id
    ).order_by(LearningResourceProgress.updated_at.desc())).all()
    return [to_dict(row) for row in rows]


@router.put("/learning/resources/{resource_id}")
def update_learning_resource(
    resource_id: int,
    req: LearningProgressRequest,
    user: User = Depends(require_roles("candidate")),
    db: Session = Depends(get_db),
):
    row = db.get(LearningResourceProgress, resource_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="学习资源不存在")
    row.progress = req.progress
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return to_dict(row)


@router.get("/governance/health")
def governance_health(db: Session = Depends(get_db)):
    """数据健康度：完整性 / 时效性 / 一致性 / 唯一性，全部来自真实库表统计。"""
    jd_total = db.scalar(select(func.count(RawJD.id))) or 0
    parsed_total = db.scalar(select(func.count(ParsedJD.id))) or 0
    duplicate_total = db.scalar(select(func.count(RawJD.id)).where(RawJD.is_duplicate.is_(True))) or 0

    # 完整性：解析结果关键字段填充率
    complete = parsed_total
    if parsed_total:
        filled = db.scalar(
            select(func.count(ParsedJD.id)).where(
                ParsedJD.domain != "未分类",
                ParsedJD.level != "未说明",
                ParsedJD.responsibilities != "[]",
                ParsedJD.required_skills != "[]",
            )
        ) or 0
        complete = filled
    completeness = round(complete / parsed_total * 100, 1) if parsed_total else 0

    # 时效性：原始 JD 的解析消化率（入库后完成解析的比例）
    timeliness = round(parsed_total / jd_total * 100, 1) if jd_total else 0

    # 一致性：通过幻觉防护（置信度 + 证据链）的比例
    guard = _guard_stats(db)
    consistency = guard["pass_rate"]

    # 唯一性：非重复原始记录占比
    uniqueness = round((jd_total - duplicate_total) / jd_total * 100, 1) if jd_total else 0

    dimensions = [
        {"key": "completeness", "label": "完整性", "value": completeness, "note": f"{complete}/{parsed_total} 条解析记录关键字段齐全"},
        {"key": "timeliness", "label": "时效性", "value": timeliness, "note": f"{parsed_total}/{jd_total} 条原始 JD 完成解析"},
        {"key": "consistency", "label": "一致性", "value": consistency, "note": f"幻觉防护通过率（取样 {guard['sample_size']} 条）"},
        {"key": "uniqueness", "label": "唯一性", "value": uniqueness, "note": f"重复入库 {duplicate_total} 条"},
    ]
    active = [d["value"] for d in dimensions]
    overall = round(sum(active) / len(active), 1) if active else 0
    return {
        "overall": overall,
        "dimensions": dimensions,
        "dataset_count": db.scalar(select(func.count(DataSource.id)).where(DataSource.status != "archived")) or 0,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/datasets")
def datasets(include_archived: bool = False, db: Session = Depends(get_db)):
    query = select(DataSource).order_by(DataSource.published_at.desc(), DataSource.id.desc())
    if not include_archived:
        query = query.where(DataSource.status != "archived")
    return [source_to_dict(row) for row in db.scalars(query).all()]


@router.get("/data-sources/status")
def data_sources_status(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return sync_status(db)


@router.post("/data-sources/sync")
def sync_data_sources(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    try:
        result = sync_official_data(db, include_network=True)
        result["validation"] = validate_source_trust(db)
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"权威数据源同步失败：{exc}") from exc


@router.get("/market/snapshot")
def get_market_snapshot(_: User = Depends(current_user), db: Session = Depends(get_db)):
    return market_snapshot(db)


@router.get("/data-sources/validation")
def get_source_validation(_: User = Depends(require_roles("admin", "hr")), db: Session = Depends(get_db)):
    return source_validation_report(db)


@router.post("/data-sources/validation/run")
def run_source_validation(_: User = Depends(require_roles("admin", "hr")), db: Session = Depends(get_db)):
    return validate_source_trust(db)


@router.get("/market/catalog")
def search_market_catalog(
    keyword: str = Query(default="", max_length=80),
    item_type: str = Query(default="", pattern="^(|occupation|skill|software_skill|essential_skill|certificate)$"),
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    query = select(ExternalCatalogItem)
    if keyword.strip():
        query = query.where(ExternalCatalogItem.name.ilike(f"%{keyword.strip()}%"))
    if item_type:
        query = query.where(ExternalCatalogItem.item_type == item_type)
    rows = db.scalars(query.order_by(ExternalCatalogItem.indexed_at.desc(), ExternalCatalogItem.id).limit(limit)).all()
    return {"items": [catalog_to_dict(row) for row in rows], "count": len(rows), "keyword": keyword, "item_type": item_type}


def _parse_optional_date(value: object) -> datetime | None:
    source = str(value or "").strip()
    if not source:
        return None
    try:
        return datetime.fromisoformat(source.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _first_value(row: dict, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _decode_jd_import(filename: str, payload: bytes) -> list[dict]:
    try:
        text_payload = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="文件必须使用 UTF-8 编码") from exc
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == ".csv":
            rows = list(csv.DictReader(io.StringIO(text_payload)))
        elif suffix == ".json":
            decoded = json.loads(text_payload)
            rows = decoded.get("items", decoded.get("data", [])) if isinstance(decoded, dict) else decoded
        else:
            raise HTTPException(status_code=400, detail="仅支持 CSV 或 JSON 文件")
    except (csv.Error, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"文件内容无法解析：{exc}") from exc
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise HTTPException(status_code=400, detail="文件内容必须是对象数组或带 items 数组的对象")
    if not rows:
        raise HTTPException(status_code=400, detail="导入文件没有数据")
    if len(rows) > 1000:
        raise HTTPException(status_code=400, detail="单次最多导入 1000 条 JD")
    return rows


def _analyze_and_persist_jd(source_text: str, db: Session, raw_jd: RawJD | None = None) -> dict:
    ai_response = analyze_with_ai("jd_parse", {"text": source_text})
    parsed = ai_response["result"]
    if "evidence_sources" not in parsed:
        parsed["evidence_sources"] = parsed.pop("evidence", [])
    parsed["ai_provider"] = ai_response["provider"]
    parsed["ai_task_type"] = ai_response["task_type"]
    rules = get_governance_rules(db)
    ok, issues = guard_payload({"confidence": parsed["confidence"], "evidence": parsed["evidence_sources"]}, rules)
    parsed["guard_status"] = "passed" if ok else "needs_review"
    parsed["guard_issues"] = issues

    content_hash = text_hash(source_text)
    deduplicated = False
    if raw_jd is None:
        raw_jd = db.scalar(select(RawJD).where(RawJD.text_hash == content_hash).order_by(RawJD.id))
        deduplicated = raw_jd is not None
        if raw_jd is None:
            raw_jd = RawJD(
                source_id=None,
                title=parsed["job_name"] or "未命名岗位",
                content=source_text,
                text_hash=content_hash,
                parse_status="processing",
                is_duplicate=False,
            )
            db.add(raw_jd)
            db.flush()

    parsed_record = ParsedJD(
        raw_jd_id=raw_jd.id,
        job_name=parsed["job_name"] or "未命名岗位",
        domain=parsed["domain"] or "未分类",
        level=parsed["level"] or "未说明",
        responsibilities=json.dumps(parsed["responsibilities"], ensure_ascii=False),
        required_skills=json.dumps(parsed["required_skills"], ensure_ascii=False),
        preferred_skills=json.dumps(parsed["preferred_skills"], ensure_ascii=False),
        tools=json.dumps(parsed["tools"], ensure_ascii=False),
        certificates=json.dumps(parsed["certificates"], ensure_ascii=False),
        experience=parsed["experience"] or "未说明",
        scenarios=json.dumps(parsed["scenarios"], ensure_ascii=False),
        confidence=float(parsed["confidence"]),
        evidence=json.dumps(
            {
                "sources": parsed["evidence_sources"],
                "guard_status": parsed["guard_status"],
                "guard_issues": issues,
                "ai_provider": ai_response["provider"],
                "ai_model": ai_response.get("model", ""),
            },
            ensure_ascii=False,
        ),
    )
    db.add(parsed_record)
    db.flush()
    raw_jd.parse_status = "parsed"
    raw_jd.parse_error = ""
    if not ok:
        db.add(
            ReviewTask(
                task_type="JD解析",
                title=parsed["job_name"],
                description="低置信度或证据不足的 JD 解析结果",
                confidence=parsed["confidence"],
                evidence=json.dumps(parsed["evidence_sources"], ensure_ascii=False),
                target_type="parsed_jd",
                target_id=parsed_record.id,
                payload_json=json.dumps({"guard_issues": issues}, ensure_ascii=False),
            )
        )
    parsed["raw_jd_id"] = raw_jd.id
    parsed["parsed_jd_id"] = parsed_record.id
    parsed["deduplicated"] = deduplicated
    return parsed


@router.post("/jd/parse")
def parse_jd(req: JDParseRequest, db: Session = Depends(get_db)):
    source_text = req.text.strip()
    if len(source_text) < 20:
        raise HTTPException(status_code=400, detail="JD 原文过短，请至少提供岗位职责和技能要求")
    parsed = _analyze_and_persist_jd(source_text, db)
    db.commit()
    return parsed


def _jd_import_batch_to_dict(db: Session, source: DataSource) -> dict:
    records = db.scalars(select(RawJD).where(RawJD.source_id == source.id).order_by(RawJD.id.desc())).all()
    status_counts: dict[str, int] = {}
    for row in records:
        status_counts[row.parse_status or "pending"] = status_counts.get(row.parse_status or "pending", 0) + 1
    metadata = json.loads(source.metadata_json or "{}")
    return {
        "id": source.id,
        "source_name": source.source_name,
        "publisher": source.publisher,
        "source_url": source.source_url,
        "license_name": source.license_name,
        "filename": metadata.get("filename", ""),
        "total_count": source.data_count,
        "imported_count": source.indexed_count,
        "duplicate_count": metadata.get("duplicate_count", 0),
        "invalid_count": metadata.get("invalid_count", 0),
        "integration": metadata.get("integration", {}),
        "status_counts": status_counts,
        "status": source.status,
        "uploaded_at": source.uploaded_at,
        "recent_records": [
            {
                "id": row.id,
                "title": row.title,
                "external_id": row.external_id,
                "source_url": row.source_url,
                "published_at": row.published_at,
                "parse_status": row.parse_status,
                "parse_error": row.parse_error,
            }
            for row in records[:5]
        ],
    }


@router.post("/jd/import")
async def import_jds(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    publisher: str = Form(...),
    source_url: str = Form(...),
    license_name: str = Form(default="公开招聘信息，仅用于研究分析"),
    auto_parse: bool = Form(default=False),
    parse_limit: int = Form(default=20),
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    if not source_name.strip() or not publisher.strip():
        raise HTTPException(status_code=400, detail="请填写数据来源名称和发布机构")
    if not source_url.strip().startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="来源主页必须是可核验的 HTTP(S) 地址")
    payload = await file.read(5 * 1024 * 1024 + 1)
    if len(payload) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="文件不能超过 5 MB")
    rows = _decode_jd_import(file.filename or "", payload)
    now = datetime.utcnow()
    normalized: list[dict] = []
    invalid_rows: list[dict] = []
    for index, row in enumerate(rows, start=2):
        title = _first_value(row, "title", "job_name", "岗位名称", "职位名称")
        content = _first_value(row, "content", "description", "jd", "job_description", "岗位描述", "职位描述")
        if len(content) < 20:
            invalid_rows.append({"row": index, "reason": "JD 正文少于 20 个字符"})
            continue
        normalized.append(
            {
                "title": title or content.splitlines()[0][:160] or "未命名岗位",
                "content": content,
                "external_id": _first_value(row, "external_id", "id", "job_id", "原始编号"),
                "source_url": _first_value(row, "source_url", "url", "job_url", "来源链接") or source_url.strip(),
                "publisher": _first_value(row, "publisher", "company", "发布机构", "企业名称") or publisher.strip(),
                "published_at": _parse_optional_date(_first_value(row, "published_at", "publish_date", "发布日期")),
            }
        )

    existing_hashes = set(db.scalars(select(RawJD.text_hash)).all())
    batch_hashes: set[str] = set()
    imported: list[RawJD] = []
    duplicate_count = 0
    source = DataSource(
        source_key=f"jd-import-{now:%Y%m%d%H%M%S}-{uuid4().hex[:8]}",
        source_name=source_name.strip(),
        publisher=publisher.strip(),
        source_url=source_url.strip(),
        license_name=license_name.strip(),
        version=f"导入于 {now:%Y-%m-%d}",
        data_type="真实岗位 JD",
        domain="多领域招聘市场",
        published_at=max((row["published_at"] for row in normalized if row["published_at"]), default=now),
        last_synced_at=now,
        uploaded_at=now,
        data_count=len(rows),
        indexed_count=0,
        duplicate_rate=0,
        noise_rate=round(len(invalid_rows) / len(rows), 4),
        quality_score=0,
        status="imported",
        sync_message="已完成文件校验、来源登记与正文哈希去重",
    )
    db.add(source)
    db.flush()
    for row in normalized:
        content_hash = text_hash(row["content"])
        if content_hash in existing_hashes or content_hash in batch_hashes:
            duplicate_count += 1
            continue
        batch_hashes.add(content_hash)
        raw = RawJD(
            source_id=source.id,
            title=row["title"][:160],
            content=row["content"],
            text_hash=content_hash,
            external_id=row["external_id"][:160],
            source_url=row["source_url"],
            publisher=row["publisher"][:160],
            published_at=row["published_at"],
            parse_status="pending",
            is_duplicate=False,
        )
        db.add(raw)
        imported.append(raw)
    db.flush()
    source.indexed_count = len(imported)
    source.duplicate_rate = round(duplicate_count / len(rows), 4)
    valid_ratio = len(imported) / len(rows)
    provenance_bonus = 5 if source.source_url.startswith("https://") else 2
    source.quality_score = round(min(100, valid_ratio * 90 + provenance_bonus), 1)
    source.metadata_json = json.dumps(
        {
            "kind": "jd_import",
            "filename": file.filename or "",
            "duplicate_count": duplicate_count,
            "invalid_count": len(invalid_rows),
            "invalid_rows": invalid_rows[:50],
            "column_contract": "title/content/source_url/external_id/published_at/publisher",
        },
        ensure_ascii=False,
    )

    parsed_count = 0
    failed_count = 0
    if auto_parse:
        for raw in imported[: max(1, min(parse_limit, 100))]:
            raw.parse_status = "processing"
            try:
                _analyze_and_persist_jd(raw.content, db, raw)
                parsed_count += 1
            except Exception as exc:
                raw.parse_status = "failed"
                raw.parse_error = str(exc)[:500]
                failed_count += 1
    pending_count = len(imported) - parsed_count - failed_count
    if imported and pending_count == 0 and failed_count == 0:
        source.status = "parsed"
    elif parsed_count or failed_count:
        source.status = "partially_parsed"
    validation = validate_source_trust(db, commit=False)
    db.commit()
    return {
        **_jd_import_batch_to_dict(db, source),
        "parsed_now": parsed_count,
        "failed_now": failed_count,
        "validation": validation,
    }


@router.get("/jd/imports")
def jd_import_history(
    _: User = Depends(require_roles("admin", "hr")),
    db: Session = Depends(get_db),
):
    sources = db.scalars(
        select(DataSource).where(DataSource.source_key.like("jd-import-%")).order_by(DataSource.id.desc())
    ).all()
    return [_jd_import_batch_to_dict(db, source) for source in sources]


@router.post("/jd/imports/{source_id}/parse")
def parse_jd_import_batch(
    source_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    source = db.get(DataSource, source_id)
    if not source or not source.source_key.startswith("jd-import-"):
        raise HTTPException(status_code=404, detail="JD 导入批次不存在")
    records = db.scalars(
        select(RawJD)
        .where(RawJD.source_id == source.id, RawJD.parse_status.in_(["pending", "failed"]))
        .order_by(RawJD.id)
        .limit(limit)
    ).all()
    parsed_count = 0
    failed_count = 0
    for raw in records:
        raw.parse_status = "processing"
        try:
            _analyze_and_persist_jd(raw.content, db, raw)
            parsed_count += 1
        except Exception as exc:
            raw.parse_status = "failed"
            raw.parse_error = str(exc)[:500]
            failed_count += 1
    remaining = db.scalar(
        select(func.count(RawJD.id)).where(RawJD.source_id == source.id, RawJD.parse_status.in_(["pending", "failed"]))
    ) or 0
    source.status = "parsed" if remaining == 0 and source.indexed_count else "partially_parsed"
    source.sync_message = f"批量解析：本次成功 {parsed_count} 条，失败 {failed_count} 条，待处理 {remaining} 条"
    db.commit()
    return {**_jd_import_batch_to_dict(db, source), "parsed_now": parsed_count, "failed_now": failed_count}


@router.post("/jd/imports/{source_id}/publish")
def publish_jd_import_batch(
    source_id: int,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    try:
        result = publish_jd_batch(db, source_id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"JD 发布到岗位能力图谱失败：{exc}") from exc

    rag_index = {"status": "skipped", "chunk_count": 0, "error": ""}
    try:
        from app.routers import rag as rag_router
        from app.services.rag.indexer import build_index

        embedder = rag_router._get_embedder()
        store = rag_router._get_stores()["jd"]
        job = build_index("jd", db, embedder, store, force_rebuild=True)
        rag_index = {"status": job.status, "chunk_count": job.chunk_count, "error": job.error_message or ""}
    except Exception as exc:
        rag_index = {"status": "failed", "chunk_count": 0, "error": str(exc)}

    source = db.get(DataSource, source_id)
    if source is not None:
        metadata = json.loads(source.metadata_json or "{}")
        metadata.setdefault("integration", {}).update({"rag_index": rag_index})
        source.metadata_json = json.dumps(metadata, ensure_ascii=False)
        source.sync_message = f"{source.sync_message}；JD 向量索引{('已刷新' if rag_index['status'] == 'success' else '刷新失败')}。"
        db.commit()
    return {**result, "rag_index": rag_index}


def _parsed_jd_to_dict(parsed: ParsedJD, raw: RawJD) -> dict:
    evidence = json.loads(parsed.evidence or "{}")
    return {
        "id": parsed.id,
        "parsed_jd_id": parsed.id,
        "raw_jd_id": raw.id,
        "job_name": parsed.job_name,
        "domain": parsed.domain,
        "level": parsed.level,
        "responsibilities": json.loads(parsed.responsibilities or "[]"),
        "required_skills": json.loads(parsed.required_skills or "[]"),
        "preferred_skills": json.loads(parsed.preferred_skills or "[]"),
        "tools": json.loads(parsed.tools or "[]"),
        "certificates": json.loads(parsed.certificates or "[]"),
        "experience": parsed.experience,
        "scenarios": json.loads(parsed.scenarios or "[]"),
        "confidence": parsed.confidence,
        "evidence_sources": evidence.get("sources", []),
        "guard_status": evidence.get("guard_status", "unknown"),
        "guard_issues": evidence.get("guard_issues", []),
        "ai_provider": evidence.get("ai_provider", ""),
        "ai_model": evidence.get("ai_model", ""),
        "source_text": raw.content,
        "source_url": raw.source_url,
        "publisher": raw.publisher,
        "external_id": raw.external_id,
        "published_at": raw.published_at,
        "parse_status": raw.parse_status,
        "created_at": raw.created_at,
    }


@router.get("/jd/history")
def jd_history(
    limit: int = Query(default=30, ge=1, le=100),
    _: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(ParsedJD, RawJD)
        .join(RawJD, RawJD.id == ParsedJD.raw_jd_id)
        .order_by(ParsedJD.id.desc())
        .limit(limit)
    ).all()
    return [_parsed_jd_to_dict(parsed, raw) for parsed, raw in rows]


@router.get("/jobs")
def jobs(db: Session = Depends(get_db)):
    return [enriched_job(db, row) for row in db.scalars(select(JobEntity).order_by(JobEntity.id)).all()]


def _next_job_version(db: Session, job_id: int) -> str:
    event_count = db.scalar(select(func.count(EvolutionEvent.id)).where(EvolutionEvent.job_id == job_id)) or 0
    return f"v{event_count + 2}.0"


@router.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    req: JobUpdateRequest,
    _: User = Depends(require_roles("admin", "hr")),
    db: Session = Depends(get_db),
):
    job = db.get(JobEntity, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    if not req.update_note.strip():
        raise HTTPException(status_code=400, detail="请填写本次更新说明")
    rules = get_governance_rules(db)
    if rules.evidence_required and not any(item.strip() for item in req.evidence_sources):
        raise HTTPException(status_code=400, detail="当前治理规则要求岗位更新必须填写证据来源")

    existing_relations = list(job.skill_relations)
    existing_required = {row.skill.name for row in existing_relations if row.relation_type == "requires"}
    existing_preferred = {row.skill.name for row in existing_relations if row.relation_type != "requires"}
    required = list(dict.fromkeys(item.strip() for item in (req.required_skills if req.required_skills is not None else existing_required) if item.strip()))
    preferred = list(dict.fromkeys(item.strip() for item in (req.preferred_skills if req.preferred_skills is not None else existing_preferred) if item.strip() and item.strip() not in required))
    if not required:
        raise HTTPException(status_code=400, detail="岗位至少需要一项必备技能")

    old_all = existing_required | existing_preferred
    new_required = set(required)
    new_preferred = set(preferred)
    new_all = new_required | new_preferred
    changed_relation = sorted(
        skill for skill in old_all & new_all
        if (skill in existing_required) != (skill in new_required)
    )
    metadata_changes = []
    for field, label in (("domain", "所属领域"), ("job_type", "岗位类型"), ("level", "岗位等级"), ("description", "岗位描述"), ("status", "状态")):
        value = getattr(req, field)
        if value is not None and value.strip() and value.strip() != getattr(job, field):
            metadata_changes.append({"skill": label, "change": f"{getattr(job, field)} → {value.strip()}"})
            setattr(job, field, value.strip())

    source_note = "；".join(item.strip() for item in req.evidence_sources if item.strip()) or "管理员人工复核"
    db.execute(delete(JobSkillRelation).where(JobSkillRelation.job_id == job.id))
    skill_by_name = {row.name: row for row in db.scalars(select(SkillEntity).where(SkillEntity.name.in_(list(new_all)))).all()}
    for relation_type, skill_names in (("requires", required), ("prefers", preferred)):
        for index, skill_name in enumerate(skill_names):
            skill = skill_by_name.get(skill_name)
            if skill is None:
                skill = SkillEntity(
                    name=skill_name,
                    category="人工复核能力",
                    description=f"{skill_name} 由人工优化流程补充到岗位能力图谱。",
                    evidence=f"人工复核来源：{source_note}",
                )
                db.add(skill)
                db.flush()
                skill_by_name[skill_name] = skill
            db.add(JobSkillRelation(
                job_id=job.id,
                skill_id=skill.id,
                relation_type=relation_type,
                weight=round(max(0.55, 1.0 - index * 0.04), 2),
                evidence=f"人工复核：{job.name} → {skill_name}；依据：{source_note}",
            ))

    previous_version = job.version
    next_version = _next_job_version(db, job.id) if rules.version_history else previous_version
    modified = metadata_changes + [
        {"skill": skill, "change": "必备能力与加分能力之间调整"}
        for skill in changed_relation
    ]
    if rules.version_history:
        event = EvolutionEvent(
            job_id=job.id,
            added_skills=json.dumps(sorted(new_all - old_all), ensure_ascii=False),
            removed_skills=json.dumps(sorted(old_all - new_all), ensure_ascii=False),
            modified_skills=json.dumps(modified, ensure_ascii=False),
            update_note=req.update_note.strip(),
            data_sources=json.dumps(req.evidence_sources or ["管理员人工复核"], ensure_ascii=False),
            confidence=1.0,
            version_record=json.dumps([previous_version, next_version], ensure_ascii=False),
            evidence=f"人工优化记录；依据：{source_note}",
        )
        job.version = next_version
        db.add(event)
    job.evidence = f"{job.evidence}\n人工优化：{req.update_note.strip()}；依据：{source_note}"
    db.commit()
    db.refresh(job)
    return enriched_job(db, job)


@router.get("/emerging-jobs")
def emerging_jobs(db: Session = Depends(get_db)):
    market = market_snapshot(db)
    skill_map = {
        "数字孪生工程技术人员": ["数字孪生", "三维建模", "仿真分析", "物联网", "数据治理"],
        "具身智能机器人应用技术员": ["机器人", "具身智能", "计算机视觉", "模型部署", "现场调试"],
        "运动数据分析师": ["统计分析", "Python", "数据可视化", "时序数据", "业务分析"],
        "智能体开发员": ["智能体编排", "大模型", "RAG", "Prompt Engineering", "API 集成"],
        "大数据专家": ["大数据", "数据治理", "Spark", "云计算", "统计分析"],
    }
    candidates = []
    for item in market["emerging_jobs"][:5]:
        candidates.append(build_emerging_candidate(
            item["name"],
            skill_map.get(item["name"], ["AI 与大数据", "技术素养", "分析性思维"]),
            item["category"],
            0.96 if item["source_key"].startswith("mohrss") else 0.90,
        ))
        candidates[-1]["source_url"] = next((source["source_url"] for source in market["sources"] if source["source_key"] == item["source_key"]), "")
        candidates[-1]["source_key"] = item["source_key"]
        candidates[-1]["publication_status"] = item["payload"].get("status", "published")
    ai_response = analyze_with_ai("emerging_job_analysis", {"candidates": candidates})
    source_by_name = {item["job_name"]: item for item in candidates}
    formal_jobs = {
        job.name: job
        for job in db.scalars(select(JobEntity).where(JobEntity.name.in_(list(source_by_name)))).all()
    }
    return [
        {
            **item,
            "job_id": formal_jobs[item["job_name"]].id if item["job_name"] in formal_jobs else None,
            "requirements": job_requirements(db, formal_jobs[item["job_name"]]) if item["job_name"] in formal_jobs else {},
            "authority": job_authority(db, formal_jobs[item["job_name"]]) if item["job_name"] in formal_jobs else {},
            "source_key": source_by_name.get(item["job_name"], {}).get("source_key", ""),
            "source_url": source_by_name.get(item["job_name"], {}).get("source_url", ""),
            "publication_status": source_by_name.get(item["job_name"], {}).get("publication_status", "published"),
            "ai_provider": ai_response["provider"],
            "ai_task_type": ai_response["task_type"],
        }
        for item in ai_response["result"]["items"]
    ]


@router.get("/job-evolution/{job_id}")
def job_evolution(job_id: int, db: Session = Depends(get_db)):
    events = db.scalars(select(EvolutionEvent).where(EvolutionEvent.job_id == job_id).order_by(EvolutionEvent.created_at)).all()
    if not events:
        raise HTTPException(status_code=404, detail="未找到岗位能力更新记录")
    event = events[-1]
    timeline = [{"time": "v1.0", "content": "初始岗位能力画像"}]
    for row in events:
        versions = parse_list(row.version_record)
        timeline.append({
            "time": versions[-1] if versions else row.created_at.strftime("%Y-%m-%d"),
            "content": row.update_note,
            "created_at": row.created_at,
            "confidence": row.confidence,
        })
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
        "timeline": timeline,
        "history_count": len(events),
    }


@router.get("/skill-graph")
def skill_graph(db: Session = Depends(get_db)):
    jobs = db.scalars(select(JobEntity)).all()
    skills = db.scalars(select(SkillEntity)).all()
    relations = db.scalars(select(JobSkillRelation)).all()
    certificates = db.scalars(select(CertificateEntity)).all()
    certificate_relations = db.scalars(select(JobCertificateRelation)).all()
    nodes = [
        {
            "id": f"job-{job.id}",
            "label": job.name,
            "type": "Job",
            "domain": job.domain,
            "level": job.level,
            "status": job.status,
            "version": job.version,
            "evidence": job.evidence,
            "authority": job_authority(db, job),
        }
        for job in jobs
    ]
    nodes += [
        {"id": f"skill-{skill.id}", "label": skill.name, "type": "Skill", "category": skill.category, "evidence": skill.evidence}
        for skill in skills
    ]
    nodes += [
        {
            "id": f"cert-{item.id}",
            "label": item.name,
            "type": "Certificate",
            "category": item.category,
            "issuer": item.issuer,
            "levels": parse_json_list(item.levels),
            "source_key": item.source_key,
            "evidence": item.evidence,
        }
        for item in certificates
    ]
    levels = sorted({job.level for job in jobs if job.level})
    nodes += [{"id": f"level-{level}", "label": level, "type": "Level", "evidence": "系统岗位画像等级标签。"} for level in levels]
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
        {
            "source": f"job-{rel.job_id}",
            "target": f"cert-{rel.certificate_id}",
            "label": rel.relation_type,
            "type": rel.relation_type,
            "weight": rel.weight,
            "evidence": rel.evidence,
        }
        for rel in certificate_relations
    ]
    edges += [
        {"source": f"job-{job.id}", "target": f"level-{job.level}", "label": "has_level", "type": "has_level", "evidence": f"{job.name} 当前岗位画像等级：{job.level}。"}
        for job in jobs if job.level
    ]

    # O*NET software examples become connected tool nodes instead of decorative isolated nodes.
    tool_nodes: dict[str, dict] = {}
    tool_edges: list[dict] = []
    jobs_by_code: dict[str, list[JobEntity]] = {}
    for job in jobs:
        code, _ = resolve_onet(job)
        jobs_by_code.setdefault(code, []).append(job)
    for code, linked_jobs in jobs_by_code.items():
        items = db.scalars(
            select(ExternalCatalogItem)
            .where(ExternalCatalogItem.source_key == "onet_30_3", ExternalCatalogItem.item_type == "software_skill", ExternalCatalogItem.external_id.like(f"{code}:%"))
            .limit(4)
        ).all()
        for item in items:
            node_id = f"tool-{item.id}"
            tool_nodes[node_id] = {"id": node_id, "label": item.name, "type": "Tool", "category": item.category, "source_key": item.source_key, "evidence": item.description}
            for job in linked_jobs:
                tool_edges.append({"source": f"job-{job.id}", "target": node_id, "label": "uses", "type": "uses", "evidence": f"O*NET 30.3 {code} 软件技能示例。"})
    nodes += list(tool_nodes.values())
    edges += tool_edges
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
    requirements = job_requirements(db, job)
    recommended_certificates = [item["name"] for item in requirements["recommended_certificates"]]
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
        recommended_certificates=recommended_certificates,
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
                "recommended_certificates": requirements["recommended_certificates"],
                "authority": job_authority(db, job),
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
            "recommended_certificates": requirements["recommended_certificates"],
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
    if not record:
        raise HTTPException(status_code=404, detail="匹配报告不存在，请先完成岗位匹配分析")
    if record and record.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权使用该匹配报告生成学习路径")
    deterministic = _safe_json_object(record.deterministic_result)
    missing = deterministic.get("missing_skills") or []
    target_job = deterministic.get("target_job") or "未命名目标岗位"
    deterministic_suggestions = deterministic.get("suggestions") or []
    recommended_certificates = deterministic.get("job_profile", {}).get("recommended_certificates", [])
    missing_certificates = deterministic.get("missing_certificates", [])
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
            "recommended_certificates": recommended_certificates,
            "missing_certificates": missing_certificates,
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
        "recommended_certificates": recommended_certificates,
        "missing_certificates": missing_certificates,
        "catalog_version": deterministic.get("job_profile", {}).get("authority", {}).get("catalog_version"),
    }


@router.get("/review-tasks")
def review_tasks(_: User = Depends(require_roles("admin", "hr")), db: Session = Depends(get_db)):
    return [to_dict(row) for row in db.scalars(select(ReviewTask).order_by(ReviewTask.created_at.desc())).all()]


@router.post("/review-tasks/{task_id}/approve", response_model=ReviewActionResponse)
def approve_task(task_id: int, _: User = Depends(require_roles("admin", "hr")), db: Session = Depends(get_db)):
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="审核任务不存在")
    if task.status != "pending":
        raise HTTPException(status_code=409, detail="审核任务已处理，不能重复提交")
    writeback = _apply_review_decision(db, task, "approved")
    task.status = "approved"
    task.resolution_note = writeback
    task.resolved_at = datetime.utcnow()
    db.commit()
    return {"id": task.id, "status": task.status, "message": f"审核已通过；{writeback}"}


@router.post("/review-tasks/{task_id}/reject", response_model=ReviewActionResponse)
def reject_task(task_id: int, _: User = Depends(require_roles("admin", "hr")), db: Session = Depends(get_db)):
    task = db.get(ReviewTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="审核任务不存在")
    if task.status != "pending":
        raise HTTPException(status_code=409, detail="审核任务已处理，不能重复提交")
    writeback = _apply_review_decision(db, task, "rejected")
    task.status = "rejected"
    task.resolution_note = writeback
    task.resolved_at = datetime.utcnow()
    db.commit()
    return {"id": task.id, "status": task.status, "message": f"审核已驳回；{writeback}"}


def _apply_review_decision(db: Session, task: ReviewTask, decision: str) -> str:
    if task.target_type == "parsed_jd" and task.target_id:
        parsed = db.get(ParsedJD, task.target_id)
        if not parsed:
            raise HTTPException(status_code=409, detail="审核目标已不存在，无法写回")
        try:
            evidence = json.loads(parsed.evidence or "{}")
        except json.JSONDecodeError:
            evidence = {"legacy_evidence": parsed.evidence}
        evidence["guard_status"] = "manual_approved" if decision == "approved" else "manual_rejected"
        evidence["review_task_id"] = task.id
        evidence["reviewed_at"] = datetime.utcnow().isoformat()
        parsed.evidence = json.dumps(evidence, ensure_ascii=False)
        return f"已写回 JD 解析记录 #{parsed.id}"
    return "该历史任务没有结构化写回目标，仅保留审核结论"


@router.get("/evaluation/metrics")
def evaluation_metrics(db: Session = Depends(get_db)):
    from app.evaluation.run_eval import run_core as run_evaluation

    empty = {
        "jd_parse_accuracy": 0,
        "resume_parse_accuracy": 0,
        "match_accuracy": 0,
        "benchmark_sample_count": 0,
        "benchmark_samples": {},
        "test_case_count": 0,
        "business_case_pass_rate": 0,
        "unit_test_coverage": None,
        "unit_test_coverage_note": "尚未生成覆盖率报告，请先运行 python -m app.evaluation.run_coverage",
        "unit_test_coverage_generated_at": None,
        "unit_test_coverage_command": "python -m app.evaluation.run_coverage",
        "competition_thresholds": {
            "accuracy_target": 90,
            "jd_sample_target": 100,
            "unit_test_coverage_target": 60,
        },
        "cases": [],
        "evaluation_error": None,
    }

    try:
        results = {item.task: item for item in run_evaluation()}
        jd_result = results["jd_extraction"]
        resume_result = results["resume_extraction"]
        match_result = results["job_match"]
        empty.update({
            "jd_parse_accuracy": round((jd_result.f1 or 0) * 100, 2),
            "resume_parse_accuracy": round((resume_result.f1 or 0) * 100, 2),
            "match_accuracy": round((match_result.accuracy or 0) * 100, 2),
            "benchmark_sample_count": sum(item.samples for item in results.values()),
            "benchmark_samples": {key: item.samples for key, item in results.items()},
        })
    except Exception as exc:  # pragma: no cover - degrade to zero metrics on failure
        empty["evaluation_error"] = f"评测脚本执行失败: {exc}"

    try:
        coverage = _coverage_summary()
        empty.update({
            "unit_test_coverage": coverage["coverage"],
            "unit_test_coverage_note": coverage["note"],
            "unit_test_coverage_generated_at": coverage["generated_at"],
            "unit_test_coverage_command": coverage["command"],
        })
    except Exception as exc:  # pragma: no cover
        empty["unit_test_coverage_note"] = f"覆盖率读取失败: {exc}"

    try:
        total = db.scalar(select(func.count(TestCase.id))) or 0
        passed = db.scalar(select(func.count(TestCase.id)).where(TestCase.passed.is_(True))) or 0
        empty.update({
            "test_case_count": total,
            "business_case_pass_rate": round(passed / total * 100, 1) if total else 0,
            "cases": [to_dict(row) for row in db.scalars(select(TestCase).limit(12)).all()],
        })
    except Exception as exc:  # pragma: no cover
        empty["evaluation_error"] = (empty.get("evaluation_error") or "") + f"; 测试用例查询失败: {exc}"

    return empty


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


def _scored_round_count(turns: list[InterviewTurn]) -> int:
    return sum(1 for turn in turns if turn.answer and turn.answer != "（已跳过）")


def _covered_interview_focus(style: str, answered_rounds: int) -> list[str]:
    plan = INTERVIEW_FOCUS_PLAN.get(style, INTERVIEW_FOCUS_PLAN["adaptive"])
    return plan[: min(answered_rounds, len(plan))]


def _next_interview_focus(style: str, answered_rounds: int) -> str:
    plan = INTERVIEW_FOCUS_PLAN.get(style, INTERVIEW_FOCUS_PLAN["adaptive"])
    return plan[min(answered_rounds, len(plan) - 1)]


def _deduplicate_interview_question(question: str, previous_questions: list[str], style: str, focus: str) -> str:
    if not previous_questions:
        return question
    if all(_question_similarity(question, previous) < 0.45 for previous in previous_questions):
        return question
    plan = INTERVIEW_FOCUS_PLAN.get(style, INTERVIEW_FOCUS_PLAN["adaptive"])
    candidates = [focus, *plan]
    for candidate_focus in candidates:
        fallback = INTERVIEW_FALLBACK_QUESTIONS.get(candidate_focus)
        if fallback and all(_question_similarity(fallback, previous) < 0.45 for previous in previous_questions):
            return fallback
    return "请换一个还没有谈过的真实经历，说明目标、你的个人行动、遇到的困难和可验证结果。"


def _question_similarity(left: str, right: str) -> float:
    left_tokens = _char_bigrams(left)
    right_tokens = _char_bigrams(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _char_bigrams(text: str) -> set[str]:
    cleaned = "".join(char for char in text if char.isalnum() or "\u4e00" <= char <= "\u9fff")
    if len(cleaned) < 2:
        return {cleaned} if cleaned else set()
    return {cleaned[index : index + 2] for index in range(len(cleaned) - 1)}


def _bounded_interview_scores(scores: dict, answer: str) -> dict[str, float]:
    if _is_low_signal_interview_answer(answer):
        return {dimension: 0.0 for dimension in INTERVIEW_DIMENSIONS}

    normalized = {}
    answer_length = len(answer.strip())
    has_evidence = any(token in answer for token in ("项目", "负责", "实现", "上线", "优化", "指标", "用户", "数据", "结果", "提升"))
    has_metric = any(char.isdigit() for char in answer)
    cap = INTERVIEW_SCORE_CEILING
    if answer_length < 12:
        cap = 55.0
    elif answer_length < 35:
        cap = 68.0
    elif not has_evidence:
        cap = 78.0
    elif not has_metric:
        cap = 86.0
    for dimension in INTERVIEW_DIMENSIONS:
        try:
            score = float(scores.get(dimension) or 0)
        except (TypeError, ValueError):
            score = INTERVIEW_SCORE_FLOOR
        normalized[dimension] = round(max(INTERVIEW_SCORE_FLOOR, min(cap, score)), 1)
    return normalized


def _is_low_signal_interview_answer(answer: str) -> bool:
    cleaned = "".join(char.lower() for char in answer.strip() if char.isalnum() or "\u4e00" <= char <= "\u9fff")
    if not cleaned:
        return True
    low_signal_phrases = (
        "不知道",
        "不会",
        "不清楚",
        "不了解",
        "没做过",
        "没有",
        "随便",
        "乱答",
        "瞎说",
        "无所谓",
        "不知道怎么说",
    )
    if cleaned in low_signal_phrases:
        return True
    if len(cleaned) <= 3 and not any("\u4e00" <= char <= "\u9fff" for char in cleaned):
        return True
    if cleaned.isdigit():
        return True
    if len(set(cleaned)) <= 2 and len(cleaned) >= 4:
        return True
    return False


def _build_final_interview_report(session: InterviewSession, turns: list[InterviewTurn]) -> dict:
    dimensions = INTERVIEW_DIMENSIONS
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
            name: max(INTERVIEW_SCORE_FLOOR, min(INTERVIEW_SCORE_CEILING, float(scores.get(name) or INTERVIEW_SCORE_FLOOR)))
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
    if overall_score >= 85:
        hiring_recommendation = "建议进入下一轮或安排核心项目复核，重点确认高分能力的稳定性。"
        readiness = "高匹配"
    elif overall_score >= 75:
        hiring_recommendation = "建议进入下一轮，围绕低分维度追加一到两个结构化追问。"
        readiness = "较匹配"
    elif overall_score >= 60:
        hiring_recommendation = "建议暂列候选池，先补充项目证据或安排针对性复试后再判断。"
        readiness = "需复核"
    else:
        hiring_recommendation = "暂不建议通过当前岗位面试，优先补齐基础能力和可验证项目经历。"
        readiness = "不匹配"

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
    weak_dimensions = [name for name in dimensions if dimension_scores[name] < 70] or list(ranked[-2:])
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
        "readiness": readiness,
        "hiring_recommendation": hiring_recommendation,
        "dimension_scores": dimension_scores,
        "summary": f"本次完成 {len(scored_rounds)} 轮有效回答，综合得分 {overall_score} 分，整体评价为“{level}”。评分区间按 {int(INTERVIEW_SCORE_FLOOR)}-{int(INTERVIEW_SCORE_CEILING)} 分控制，短答和缺少证据的回答会限制得分上限。",
        "strengths": [strength_text[name] for name in ranked[:2]],
        "improvements": [improvement_text[name] for name in weak_dimensions[:3]],
        "next_steps": [
            f"围绕“{name}”准备一个可复述案例：背景、个人行动、关键取舍、量化结果各一句。"
            for name in weak_dimensions[:3]
        ],
        "trend": trend,
        "rounds_scored": len(scored_rounds),
        "target_rounds": INTERVIEW_TARGET_SCORED_ROUNDS,
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
        completeness=0,
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
