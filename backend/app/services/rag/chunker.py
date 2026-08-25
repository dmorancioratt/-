"""文本切分器：把不同数据源的 ORM 实体切成 RawChunk。"""

from __future__ import annotations

from app.models import CandidateProfile, JobEntity, JobSkillRelation, RawJD, Resume, ResumeSkill, SkillEntity
from app.services.rag.models import RawChunk


def _safe_text(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def chunk_jd(raw_jd: RawJD, *, parsed: dict | None = None) -> list[RawChunk]:
    """整条 JD 原文作为一段；parsed 字典（来自 ParsedJD）作为可选附加元数据。"""
    text = _safe_text(raw_jd.content)
    if not text:
        return []
    # 把 title 和 source_url 也拼到 text 前缀，方便检索时命中岗位名
    parts: list[str] = []
    if raw_jd.title:
        parts.append(f"岗位名称：{raw_jd.title}")
    parts.append(text)
    if raw_jd.publisher:
        parts.append(f"来源：{raw_jd.publisher}")
    full_text = "\n".join(parts)
    meta: dict = {
        "title": raw_jd.title or "",
        "publisher": raw_jd.publisher or "",
        "text_hash": raw_jd.text_hash or "",
        "parse_status": raw_jd.parse_status or "",
    }
    if parsed:
        for key in ("job_name", "domain", "level", "required_skills", "preferred_skills", "tools"):
            value = parsed.get(key)
            if value:
                meta[key] = value
    return [
        RawChunk(
            source_type="jd",
            ref_id=int(raw_jd.id),
            text=full_text,
            metadata=meta,
        )
    ]


def chunk_job_skill(
    job: JobEntity,
    rel: JobSkillRelation,
    skill: SkillEntity,
) -> list[RawChunk]:
    """一条岗位-技能关系 = 一条 chunk，方便做关系型证据检索。"""
    skill_name = _safe_text(skill.name)
    job_name = _safe_text(job.name)
    text = (
        f"岗位「{job_name}」与技能「{skill_name}」的关系："
        f"关系类型={rel.relation_type or 'requires'}；"
        f"权重={rel.weight or 0:.2f}。"
        f"岗位领域={job.domain or '未分类'}；岗位级别={job.level or '未说明'}。"
        f"技能分类={skill.category or '未分类'}。"
    )
    if skill.description:
        text += f"\n技能描述：{skill.description[:300]}"
    if job.description:
        text += f"\n岗位描述：{job.description[:300]}"
    meta = {
        "job_name": job_name,
        "skill_name": skill_name,
        "domain": job.domain or "",
        "level": job.level or "",
        "relation_type": rel.relation_type or "requires",
        "weight": float(rel.weight or 0),
        "skill_category": skill.category or "",
    }
    return [
        RawChunk(
            source_type="job_skill",
            ref_id=int(rel.id),
            text=text,
            metadata=meta,
        )
    ]


def chunk_skill(skill: SkillEntity) -> list[RawChunk]:
    name = _safe_text(skill.name)
    desc = _safe_text(skill.description)
    text = f"技能名称：{name}\n分类：{skill.category or '未分类'}\n描述：{desc or '（暂无描述）'}"
    meta = {
        "skill_name": name,
        "skill_category": skill.category or "",
    }
    return [
        RawChunk(
            source_type="skill",
            ref_id=int(skill.id),
            text=text,
            metadata=meta,
        )
    ]


def _split_paragraphs(text: str, max_len: int = 500) -> list[str]:
    """把长文本按段落切分，单段上限 max_len。"""
    if not text:
        return []
    parts: list[str] = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        while len(para) > max_len:
            parts.append(para[:max_len])
            para = para[max_len:]
        parts.append(para)
    return parts


def _list_from_json_field(value: object | None) -> list[str]:
    """解析 ORM 中以 JSON 字符串存储的列表字段（兼容 list / str / '[...]' / 'a,b'）。"""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    import ast

    text = str(value).strip()
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (SyntaxError, ValueError):
        pass
    if "," in text:
        return [item.strip() for item in text.strip("[]").split(",") if item.strip()]
    return [text] if text else []


def chunk_candidate(
    profile: CandidateProfile | None,
    resume: Resume,
    resume_skills: list[ResumeSkill],
) -> list[RawChunk]:
    """候选人 = 画像（技能/证书/项目/实习）+ 简历原文（按段落切）。"""
    chunks: list[RawChunk] = []

    candidate_name = _safe_text(resume.name) or _safe_text(getattr(profile, "display_name", None) if profile else None)

    skills = _list_from_json_field(profile.skills) if profile else []
    certificates = _list_from_json_field(profile.certificates) if profile else []
    projects = _list_from_json_field(profile.projects) if profile else []
    internships = _list_from_json_field(profile.internships) if profile else []
    awards = _list_from_json_field(profile.awards) if profile else []

    if skills:
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」掌握的技能：\n" + "\n".join(f"- {s}" for s in skills),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "skills",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )
    if certificates:
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」的证书：\n" + "\n".join(f"- {c}" for c in certificates),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "certificates",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )
    if projects:
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」的项目经历：\n" + "\n".join(f"- {p}" for p in projects),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "projects",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )
    if internships:
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」的实习经历：\n" + "\n".join(f"- {i}" for i in internships),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "internships",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )
    if awards:
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」的获奖与竞赛：\n" + "\n".join(f"- {a}" for a in awards),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "awards",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )
    if resume_skills:
        lines = []
        for rs in resume_skills:
            name = _safe_text(rs.skill_name)
            level = _safe_text(rs.level) or "未说明"
            evi = _safe_text(rs.evidence)
            line = f"- {name}（{level}）"
            if evi:
                line += f"；证据：{evi[:80]}"
            lines.append(line)
        chunks.append(
            RawChunk(
                source_type="candidate",
                ref_id=int(resume.id),
                text=f"候选人「{candidate_name or '匿名'}」的简历技能与等级：\n" + "\n".join(lines),
                metadata={
                    "candidate_name": candidate_name,
                    "field": "resume_skills",
                    "user_id": int(resume.user_id) if resume.user_id else 0,
                },
            )
        )

    raw_text = _safe_text(resume.raw_text)
    if raw_text:
        for idx, para in enumerate(_split_paragraphs(raw_text)):
            chunks.append(
                RawChunk(
                    source_type="candidate",
                    ref_id=int(resume.id),
                    text=para,
                    metadata={
                        "candidate_name": candidate_name,
                        "field": "resume_paragraph",
                        "paragraph_index": idx,
                        "user_id": int(resume.user_id) if resume.user_id else 0,
                    },
                )
            )

    return chunks