from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select

from app.db.database import SessionLocal
from app.models import (
    CandidateProfile,
    InterviewSession,
    InterviewTurn,
    JobEntity,
    LearningResourceProgress,
    LearningTask,
    MatchAnalysisRecord,
    ParsedJD,
    RagDocument,
    RawJD,
    Resume,
    ResumeSkill,
    ReviewTask,
    TestCase,
    User,
    WorkflowConfig,
)
from app.services.auth import hash_password
from app.services.jd_parser import text_hash
from app.services.matching import score_match


PASSWORD = "Data@2026"
ACCOUNT_SPECS = (
    ("student_data01", "candidate", "林晓舟", "杭州电子科技大学"),
    ("hr_data01", "hr", "周敏", "数融科技有限公司"),
    ("admin_data01", "admin", "平台管理员", "数融智联平台"),
)
MARKER = "data-account-demo-v1"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def upsert_user(db, username: str, role: str, display_name: str, organization: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(username=username)
        db.add(user)
        db.flush()
    user.password_hash = hash_password(PASSWORD)
    user.role = role
    user.display_name = display_name
    user.email = f"{username}@shurong.local"
    user.phone = "13800002026"
    user.organization = organization
    user.status = "active"
    return user


def seed_candidate(db, user: User) -> dict[str, int]:
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    if profile is None:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
    profile.real_name = "林晓舟"
    profile.education = "本科"
    profile.major = "计算机科学与技术"
    profile.school = "杭州电子科技大学"
    profile.target_role = "大模型应用工程师"
    profile.city = "浙江省/杭州市"
    profile.expected_salary = "15k-22k"
    profile.skills = json_text(["Python", "FastAPI", "RAG", "LangChain", "SQL", "Docker", "Git", "ECharts"])
    profile.certificates = json_text(["软件设计师", "大学英语六级"])
    profile.projects = json_text([
        "企业知识库问答系统：负责文档切片、向量检索、引用校验和效果评估，测试集命中率提升至 88%",
        "岗位能力图谱平台：完成技能实体抽取、关系构建和 ECharts 可视化",
    ])
    profile.internships = json_text(["数融科技 AI 平台研发实习：参与 RAG 服务接口和质量监控开发"])
    profile.awards = json_text(["全国大学生软件创新大赛省级一等奖"])
    profile.self_summary = "具备 AI 应用、后端服务和数据可视化项目经验，能够完成从需求分析到部署验证的完整交付。"
    profile.completeness = 96
    profile.updated_at = utcnow()
    db.flush()

    source_filename = f"{MARKER}-student-resume.txt"
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id, Resume.source_filename == source_filename))
    if resume is None:
        resume = Resume(
            user_id=user.id,
            source_filename=source_filename,
            name=profile.real_name,
            education=profile.education,
            major=profile.major,
            school=profile.school,
            projects="",
            internships="",
            certificates="",
            competitions="",
            intention=profile.target_role,
            raw_text="",
        )
        db.add(resume)
    resume.name = profile.real_name
    resume.education = profile.education
    resume.major = profile.major
    resume.school = profile.school
    resume.projects = "企业知识库问答系统；岗位能力图谱平台；招聘 JD 可信度交叉验证模块"
    resume.internships = "数融科技 AI 平台研发实习，负责 FastAPI 接口、RAG 检索链路与质量指标看板"
    resume.certificates = "软件设计师；大学英语六级"
    resume.competitions = "全国大学生软件创新大赛省级一等奖"
    resume.intention = "大模型应用工程师"
    resume.raw_text = "林晓舟，本科计算机科学与技术。熟悉 Python、FastAPI、RAG、LangChain、SQL、Docker、Git 与 ECharts。完成企业知识库问答和岗位能力图谱项目。"
    resume.created_at = utcnow() - timedelta(days=18)
    db.flush()

    db.execute(delete(ResumeSkill).where(ResumeSkill.resume_id == resume.id))
    skill_levels = {
        "Python": "高级", "FastAPI": "中级", "RAG": "中级", "LangChain": "中级",
        "SQL": "中级", "Docker": "中级", "Git": "高级", "ECharts": "中级",
    }
    for name, level in skill_levels.items():
        db.add(ResumeSkill(resume_id=resume.id, skill_name=name, level=level, evidence=f"{MARKER}: 简历项目与技能描述"))

    job = db.scalar(select(JobEntity).where(JobEntity.name == "大模型应用工程师"))
    if job is None:
        job = db.scalar(select(JobEntity).order_by(JobEntity.id))
    if job is None:
        raise RuntimeError("数据库中没有岗位，无法生成匹配数据")

    relations = sorted(job.skill_relations, key=lambda item: item.weight, reverse=True)
    required = [item.skill.name for item in relations if item.relation_type == "requires"]
    preferred = [item.skill.name for item in relations if item.relation_type == "prefers"]
    result = score_match(
        list(skill_levels), required, preferred, ["软件设计师", "大学英语六级"],
        projects=json.loads(profile.projects), internships=json.loads(profile.internships),
        awards=json.loads(profile.awards), education=profile.education, major=profile.major,
        self_summary=profile.self_summary, job_name=job.name, job_description=job.description,
        job_domain=job.domain, job_level=job.level,
        required_weights={item.skill.name: item.weight for item in relations if item.relation_type == "requires"},
        preferred_weights={item.skill.name: item.weight for item in relations if item.relation_type == "prefers"},
    )
    result.update({
        "target_job": job.name,
        "target_job_id": job.id,
        "job_profile": {
            "name": job.name, "domain": job.domain, "level": job.level,
            "job_type": job.job_type, "description": job.description,
            "required_skills": required, "preferred_skills": preferred,
            "recommended_certificates": [],
        },
        "candidate": {
            "name": profile.real_name, "source_type": "resume", "resume_id": resume.id,
            "education": profile.education, "major": profile.major, "school": profile.school,
        },
    })
    ai_analysis = {
        "summary": "候选人的 Python、RAG 与后端工程经验和目标岗位高度相关，已有项目证据可支撑核心能力。",
        "strengths": ["具备端到端 RAG 项目经验", "能够结合 FastAPI 与 Docker 完成工程落地"],
        "suggestions": ["补充向量数据库性能对比实验", "完善模型评测与线上可观测性证据"],
        "interview_questions": ["请说明 RAG 召回率的评测方法", "如何定位检索结果相关但答案错误的问题"],
    }
    record = db.scalar(select(MatchAnalysisRecord).where(
        MatchAnalysisRecord.user_id == user.id,
        MatchAnalysisRecord.candidate_name == profile.real_name,
    ))
    if record is None:
        record = MatchAnalysisRecord(user_id=user.id, job_id=job.id)
        db.add(record)
        db.flush()
    record.resume_id = resume.id
    record.job_id = job.id
    record.candidate_name = profile.real_name
    record.source_type = "resume"
    record.total_score = result["total_score"]
    record.deterministic_result = json_text(result)
    record.ai_analysis = json_text(ai_analysis)
    record.ai_provider = "demo_verified"
    record.ai_model = "preset-evidence"
    record.created_at = utcnow() - timedelta(days=3)
    db.flush()

    db.execute(delete(LearningTask).where(LearningTask.user_id == user.id))
    db.execute(delete(LearningResourceProgress).where(LearningResourceProgress.user_id == user.id))
    learning_rows = [
        ("完成向量数据库选型对比", "对比 FAISS、Milvus 的索引效率和检索质量", "向量数据库", 75, "completed"),
        ("补充 RAG 评测实验", "建立召回率、答案忠实度和引用准确率测试集", "RAG 评测", 55, "pending"),
        ("完成容器化部署复盘", "整理 Docker 部署、监控和故障排查过程", "Docker 部署", 35, "pending"),
    ]
    for index, (title, description, skill_name, progress, status) in enumerate(learning_rows):
        completed_at = utcnow() - timedelta(days=2) if status == "completed" else None
        db.add(LearningTask(
            user_id=user.id, source_report_id=record.id, title=title, description=description,
            status=status, completed_at=completed_at, created_at=utcnow() - timedelta(days=8-index),
        ))
        db.add(LearningResourceProgress(
            user_id=user.id, source_report_id=record.id, skill_name=skill_name,
            title=f"{skill_name}专题学习与项目实践", progress=progress,
        ))

    session = db.scalar(select(InterviewSession).where(InterviewSession.user_id == user.id, InterviewSession.job_name == job.name))
    if session is None:
        session = InterviewSession(user_id=user.id, job_name=job.name)
        db.add(session)
        db.flush()
    session.interview_style = "project"
    session.resume_summary = "具备 Python、RAG、FastAPI、Docker 项目经验，目标岗位为大模型应用工程师。"
    session.status = "completed"
    session.round_count = 3
    session.final_score = 84.6
    session.final_report = json_text({
        "overall_score": 84.6, "level": "表现良好",
        "dimension_scores": {"专业能力": 87, "项目表达": 84, "岗位匹配": 86, "逻辑沟通": 78},
        "summary": "技术方案和项目结果表达完整，建议进一步强化指标口径与异常处理细节。",
        "strengths": ["RAG 项目链路完整", "工程落地能力较强"],
        "improvements": ["回答时先给结论", "补充线上监控指标"],
        "trend": "三轮回答整体稳定，项目细节逐步充分。", "rounds_scored": 3,
    })
    session.completed_at = utcnow() - timedelta(days=1)
    session.created_at = utcnow() - timedelta(days=1, hours=1)
    session.updated_at = utcnow() - timedelta(days=1)
    db.flush()
    db.execute(delete(InterviewTurn).where(InterviewTurn.session_id == session.id))
    turns = [
        (1, "请介绍你负责的 RAG 项目。", "我负责文档切片、向量检索、引用校验与测试集评测，将命中率提升到 88%。", "项目结构完整，量化结果明确。", {"专业能力": 86, "项目表达": 84, "岗位匹配": 87, "逻辑沟通": 80}),
        (2, "如何降低大模型幻觉？", "先通过混合检索提高召回，再做重排和引用校验；低置信度结果进入人工复核。", "覆盖了检索、校验和人工闭环。", {"专业能力": 89, "项目表达": 83, "岗位匹配": 88, "逻辑沟通": 79}),
        (3, "如何验证系统上线后的质量？", "持续监控召回率、引用准确率、答案忠实度、响应时间和失败率，并保留回归集。", "指标体系较完整。", {"专业能力": 86, "项目表达": 85, "岗位匹配": 84, "逻辑沟通": 76}),
    ]
    for round_number, question, answer, feedback, scores in turns:
        db.add(InterviewTurn(
            session_id=session.id, round_number=round_number, question=question, answer=answer,
            feedback=feedback, follow_up_basis="根据上一轮回答和岗位核心能力继续追问",
            score_preview=json_text(scores),
        ))
    return {"profile": profile.id, "resume": resume.id, "report": record.id, "interview": session.id}


def seed_shared_business_data(db, admin: User) -> dict[str, int]:
    job = db.scalar(select(JobEntity).where(JobEntity.name == "大模型应用工程师")) or db.scalar(select(JobEntity).order_by(JobEntity.id))
    if job is None:
        raise RuntimeError("数据库中没有岗位，无法生成业务数据")

    raw = db.scalar(select(RawJD).where(RawJD.external_id == MARKER))
    jd_content = "大模型应用工程师，负责企业知识库、RAG 检索链路、智能体工作流和效果评测。要求熟悉 Python、FastAPI、向量数据库、Docker，能够建立召回率、忠实度与引用准确率指标。"
    if raw is None:
        raw = RawJD(external_id=MARKER, title=job.name, content=jd_content, text_hash=text_hash(jd_content))
        db.add(raw)
        db.flush()
    raw.source_url = "local://data-account-demo/jd-001"
    raw.publisher = "数融科技有限公司"
    raw.published_at = utcnow() - timedelta(days=7)
    raw.parse_status = "parsed"
    raw.is_duplicate = False
    raw.created_at = utcnow() - timedelta(days=7)

    parsed = db.scalar(select(ParsedJD).where(ParsedJD.raw_jd_id == raw.id))
    if parsed is None:
        parsed = ParsedJD(raw_jd_id=raw.id)
        db.add(parsed)
    parsed.job_name = job.name
    parsed.domain = job.domain
    parsed.level = job.level
    parsed.responsibilities = json_text(["建设 RAG 检索链路", "开发智能体工作流", "建立效果评测与监控"])
    parsed.required_skills = json_text(["Python", "FastAPI", "RAG", "向量数据库", "Docker"])
    parsed.preferred_skills = json_text(["LangChain", "模型评测", "Kubernetes"])
    parsed.tools = json_text(["Git", "Docker", "Linux"])
    parsed.certificates = json_text(["软件设计师"])
    parsed.experience = "1-3 年"
    parsed.scenarios = json_text(["企业知识库", "招聘智能体"])
    parsed.confidence = 0.92
    parsed.evidence = f"{MARKER}: 本地演示 JD 解析结果"

    review = db.scalar(select(ReviewTask).where(ReviewTask.evidence == f"{MARKER}: cross-validation"))
    if review is None:
        review = ReviewTask(evidence=f"{MARKER}: cross-validation")
        db.add(review)
    review.task_type = "source_validation"
    review.title = "招聘 JD 多源交叉验证复核"
    review.description = "同一岗位在企业官网与招聘平台的技能要求存在差异，需要确认向量数据库和模型评测权重。"
    review.confidence = 0.71
    review.status = "pending"
    review.target_type = "raw_jd"
    review.target_id = raw.id
    review.payload_json = json_text({"duplicate_score": 0.18, "noise_score": 0.08, "time_decay_weight": 0.93})

    cases = (
        ("算法测试", "JD 技能抽取准确率", "准确率不低于 85%", "抽样 40 条，准确率 90%"),
        ("智能体测试", "RAG 引用忠实度", "忠实度不低于 90%", "测试集忠实度 93%"),
        ("交叉验证", "多数据源一致性", "关键技能一致率不低于 80%", "三个来源一致率 86%"),
    )
    for case_type, name, expected, actual in cases:
        case = db.scalar(select(TestCase).where(TestCase.name == f"{MARKER}-{name}"))
        if case is None:
            case = TestCase(name=f"{MARKER}-{name}")
            db.add(case)
        case.case_type = case_type
        case.expected = expected
        case.actual = actual
        case.passed = True

    upload_root = Path(__file__).resolve().parents[1] / "backend" / "data" / "rag_uploads"
    upload_root.mkdir(parents=True, exist_ok=True)
    document_path = upload_root / f"{MARKER}-rag-knowledge.md"
    document_text = "# RAG 质量规范\n\n所有答案必须引用检索证据。低于 0.72 的置信度结果进入人工复核。评测至少包含召回率、答案忠实度、引用准确率和响应时间。\n"
    document_path.write_text(document_text, encoding="utf-8")
    doc = db.scalar(select(RagDocument).where(RagDocument.filename == document_path.name))
    if doc is None:
        doc = RagDocument(filename=document_path.name)
        db.add(doc)
    doc.file_type = "md"
    doc.char_count = len(document_text)
    doc.chunk_count = 0
    doc.indexed = False
    doc.uploaded_by = admin.id
    doc.storage_path = str(document_path)

    workflow = db.scalar(select(WorkflowConfig).where(WorkflowConfig.name == "演示账号 RAG 防幻觉流程"))
    if workflow is None:
        workflow = WorkflowConfig(name="演示账号 RAG 防幻觉流程")
        db.add(workflow)
    workflow.is_default = False
    workflow.graph_json = json_text({
        "nodes": [
            {"id": "node-input", "type": "input", "position": {"x": 80, "y": 160}, "data": {"kind": "input", "label": "用户问题", "description": "接收用户原始提问", "status": "idle", "config": {}}},
            {"id": "node-retrieve", "type": "retrieve", "position": {"x": 320, "y": 160}, "data": {"kind": "retrieve", "label": "Top-K 检索", "description": "从本地知识库召回证据", "status": "idle", "config": {"top_k": 5}}},
            {"id": "node-guard", "type": "guard", "position": {"x": 560, "y": 160}, "data": {"kind": "guard", "label": "幻觉检测", "description": "执行事实一致性与置信度校验", "status": "idle", "config": {"threshold": 0.72}}},
            {"id": "node-output", "type": "output", "position": {"x": 800, "y": 160}, "data": {"kind": "output", "label": "最终回答", "description": "返回带引用的可信答案", "status": "idle", "config": {}}},
        ],
        "edges": [
            {"id": "edge-1", "source": "node-input", "target": "node-retrieve", "animated": False},
            {"id": "edge-2", "source": "node-retrieve", "target": "node-guard", "animated": False},
            {"id": "edge-3", "source": "node-guard", "target": "node-output", "animated": False},
        ],
    })
    workflow.node_settings = json_text({"retrieve": {"top_k": 5}, "guard": {"threshold": 0.72}})
    workflow.updated_at = utcnow()
    db.flush()
    return {"raw_jd": raw.id, "review": review.id, "rag_document": doc.id, "workflow": workflow.id}


def main() -> None:
    db = SessionLocal()
    try:
        accounts = {}
        for username, role, display_name, organization in ACCOUNT_SPECS:
            accounts[role] = upsert_user(db, username, role, display_name, organization)
        db.flush()
        candidate_data = seed_candidate(db, accounts["candidate"])
        shared_data = seed_shared_business_data(db, accounts["admin"])
        db.commit()
        print(json.dumps({
            "accounts": [
                {"username": username, "password": PASSWORD, "role": role, "display_name": display_name}
                for username, role, display_name, _ in ACCOUNT_SPECS
            ],
            "candidate_data": candidate_data,
            "shared_business_data": shared_data,
        }, ensure_ascii=False, indent=2))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
