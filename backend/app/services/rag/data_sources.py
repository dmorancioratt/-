"""从 SQLite 抽取各类数据源并切分成 RawChunk 迭代器。"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    CandidateProfile,
    JobEntity,
    JobSkillRelation,
    ParsedJD,
    RawJD,
    Resume,
    ResumeSkill,
    SkillEntity,
)
from app.services.rag.chunker import chunk_candidate, chunk_jd, chunk_job_skill, chunk_skill
from app.services.rag.models import RawChunk


def iter_jd_chunks(db: Session) -> Iterator[RawChunk]:
    """所有 RawJD 各取一段；附带同名 ParsedJD 的解析字段作为元数据。"""
    raw_jds = db.scalars(select(RawJD).order_by(RawJD.id)).all()
    parsed_lookup: dict[int, ParsedJD] = {
        p.raw_jd_id: p for p in db.scalars(select(ParsedJD).where(ParsedJD.raw_jd_id.is_not(None))).all() if p.raw_jd_id
    }
    for raw in raw_jds:
        parsed = parsed_lookup.get(raw.id)
        parsed_dict = None
        if parsed is not None:
            parsed_dict = {
                "job_name": parsed.job_name or "",
                "domain": parsed.domain or "",
                "level": parsed.level or "",
                "required_skills": parsed.required_skills or "",
                "preferred_skills": parsed.preferred_skills or "",
                "tools": parsed.tools or "",
            }
        yield from chunk_jd(raw, parsed=parsed_dict)


def iter_skill_chunks(db: Session) -> Iterator[RawChunk]:
    skills = db.scalars(select(SkillEntity).order_by(SkillEntity.id)).all()
    for skill in skills:
        yield from chunk_skill(skill)


def iter_job_skill_chunks(db: Session) -> Iterator[RawChunk]:
    """所有岗位-技能关系各取一段。需要 join。"""
    rows = db.execute(
        select(JobEntity, JobSkillRelation, SkillEntity)
        .join(JobSkillRelation, JobSkillRelation.job_id == JobEntity.id)
        .join(SkillEntity, SkillEntity.id == JobSkillRelation.skill_id)
        .order_by(JobEntity.id, JobSkillRelation.id)
    ).all()
    for job, rel, skill in rows:
        yield from chunk_job_skill(job, rel, skill)


def iter_candidate_chunks(db: Session) -> Iterator[RawChunk]:
    """所有 Resume + 关联的 CandidateProfile + ResumeSkill。"""
    resumes = db.scalars(select(Resume).order_by(Resume.id)).all()
    profiles_by_user = {p.user_id: p for p in db.scalars(select(CandidateProfile)).all()}
    skills_by_resume: dict[int, list[ResumeSkill]] = {}
    for rs in db.scalars(select(ResumeSkill).order_by(ResumeSkill.resume_id)).all():
        skills_by_resume.setdefault(rs.resume_id, []).append(rs)
    for resume in resumes:
        profile = profiles_by_user.get(resume.user_id) if resume.user_id else None
        rs_skills = skills_by_resume.get(resume.id, [])
        yield from chunk_candidate(profile, resume, rs_skills)