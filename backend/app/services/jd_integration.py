"""Publish verified parsed JD batches into the canonical job capability graph."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    DataSource,
    EvolutionEvent,
    JobEntity,
    JobSkillRelation,
    ParsedJD,
    RawJD,
    SkillEntity,
)
from app.services.hallucination_guard import get_governance_rules


INVALID_JOB_NAMES = {"未命名岗位", "未识别岗位", "未知岗位", "岗位", "职位"}
UNKNOWN_VALUES = {"", "未分类", "未说明", "未知"}


def _list(value: str | None) -> list[str]:
    try:
        raw = json.loads(value or "[]")
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(raw, list):
        return []
    return list(dict.fromkeys(str(item).strip()[:120] for item in raw if str(item).strip()))


def _evidence(value: str | None) -> dict[str, Any]:
    try:
        raw = json.loads(value or "{}")
    except (json.JSONDecodeError, TypeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _job_key(name: str) -> str:
    return re.sub(r"[\s\-_—]+", "", name).casefold()


def _valid_job_name(name: str) -> bool:
    clean = name.strip()
    return len(clean) >= 3 and clean not in INVALID_JOB_NAMES


def _majority(values: list[str], default: str) -> str:
    usable = [value.strip() for value in values if value and value.strip() not in UNKNOWN_VALUES]
    return Counter(usable).most_common(1)[0][0] if usable else default


def _next_version(job: JobEntity, db: Session) -> str:
    event_count = db.scalar(
        select(func.count(EvolutionEvent.id)).where(EvolutionEvent.job_id == job.id)
    ) or 0
    return f"v{event_count + 2}.0"


def publish_jd_batch(db: Session, source_id: int) -> dict[str, Any]:
    """Merge trustworthy parsed rows into jobs and skills without deleting existing data."""
    source = db.get(DataSource, source_id)
    if source is None or not source.source_key.startswith("jd-import-"):
        raise ValueError("JD 导入批次不存在")

    rows = db.execute(
        select(ParsedJD, RawJD)
        .join(RawJD, ParsedJD.raw_jd_id == RawJD.id)
        .where(RawJD.source_id == source.id, RawJD.parse_status == "parsed")
        .order_by(ParsedJD.id)
    ).all()
    rules = get_governance_rules(db)
    groups: dict[str, list[tuple[ParsedJD, RawJD]]] = defaultdict(list)
    skipped: list[dict[str, Any]] = []

    for parsed, raw in rows:
        evidence = _evidence(parsed.evidence)
        skills = _list(parsed.required_skills) + _list(parsed.preferred_skills) + _list(parsed.tools)
        reason = ""
        if evidence.get("guard_status") != "passed" or float(parsed.confidence or 0) < rules.confidence_threshold:
            reason = "未通过防幻觉可信校验"
        elif not _valid_job_name(parsed.job_name or ""):
            reason = "岗位名称无效"
        elif not skills:
            reason = "未提取到岗位能力"
        if reason:
            skipped.append({"parsed_jd_id": parsed.id, "title": raw.title, "reason": reason})
            continue
        groups[_job_key(parsed.job_name)].append((parsed, raw))

    jobs_by_key = {_job_key(job.name): job for job in db.scalars(select(JobEntity)).all()}
    skills_by_name = {skill.name: skill for skill in db.scalars(select(SkillEntity)).all()}
    created_jobs = 0
    updated_jobs = 0
    created_skills = 0
    added_relations = 0
    upgraded_relations = 0
    evolution_events = 0
    published_parsed_ids: list[int] = []
    source_label = f"{source.source_name}（批次 #{source.id}）"
    source_marker = f"JD_IMPORT_SOURCE_{source.id}"

    for key, group in groups.items():
        parsed_rows = [item[0] for item in group]
        raw_rows = [item[1] for item in group]
        canonical_name = Counter(item.job_name.strip() for item in parsed_rows).most_common(1)[0][0]
        required = list(dict.fromkeys(skill for item in parsed_rows for skill in _list(item.required_skills)))
        preferred = list(dict.fromkeys(
            skill
            for item in parsed_rows
            for skill in (_list(item.preferred_skills) + _list(item.tools))
            if skill not in required
        ))
        domain = _majority([item.domain for item in parsed_rows], "其他")
        level = _majority([item.level for item in parsed_rows], "未说明")
        responsibilities = list(dict.fromkeys(
            text for item in parsed_rows for text in _list(item.responsibilities)
        ))
        confidence = round(sum(float(item.confidence or 0) for item in parsed_rows) / len(parsed_rows), 3)
        evidence_urls = list(dict.fromkeys(raw.source_url for raw in raw_rows if raw.source_url))
        evidence_note = (
            f"{source_marker}；来自 {source_label} 的 {len(group)} 条真实 JD；"
            f"平均解析置信度 {confidence:.1%}；来源：{'、'.join(evidence_urls[:3]) or source.source_url}"
        )

        job = jobs_by_key.get(key)
        is_new = job is None
        if job is None:
            job = JobEntity(
                name=canonical_name,
                domain=domain,
                job_type="真实 JD 归纳岗位",
                level=level,
                description="；".join(responsibilities[:5]) or f"由 {source_label} 真实 JD 汇总生成。",
                is_emerging=False,
                status="active",
                version="v1.0",
                evidence=evidence_note,
            )
            db.add(job)
            db.flush()
            jobs_by_key[key] = job
            created_jobs += 1
        else:
            updated_jobs += 1
            if job.domain in UNKNOWN_VALUES:
                job.domain = domain
            if job.level in UNKNOWN_VALUES:
                job.level = level
            if source_marker not in (job.evidence or ""):
                job.evidence = f"{job.evidence}\n{evidence_note}".strip()

        existing = {
            relation.skill.name: relation
            for relation in db.scalars(
                select(JobSkillRelation).where(JobSkillRelation.job_id == job.id)
            ).all()
        }
        added: list[str] = []
        modified: list[dict[str, str]] = []
        for relation_type, names in (("requires", required), ("prefers", preferred)):
            for index, name in enumerate(names):
                skill = skills_by_name.get(name)
                if skill is None:
                    skill = SkillEntity(
                        name=name,
                        category="真实 JD 能力",
                        description=f"从真实招聘 JD 中提取的岗位能力：{name}。",
                        evidence=evidence_note,
                    )
                    db.add(skill)
                    db.flush()
                    skills_by_name[name] = skill
                    created_skills += 1
                relation = existing.get(name)
                if relation is None:
                    relation = JobSkillRelation(
                        job_id=job.id,
                        skill_id=skill.id,
                        relation_type=relation_type,
                        weight=round(max(0.55, 1.0 - index * 0.04), 2),
                        evidence=f"{canonical_name} → {name}；{evidence_note}",
                    )
                    db.add(relation)
                    existing[name] = relation
                    added.append(name)
                    added_relations += 1
                elif relation_type == "requires" and relation.relation_type != "requires":
                    relation.relation_type = "requires"
                    relation.evidence = f"{relation.evidence}\n由 {source_label} 真实 JD 更新为必备能力。".strip()
                    modified.append({"skill": name, "change": "由加分能力更新为必备能力"})
                    upgraded_relations += 1

        if added or modified or is_new:
            previous_version = "v0.0" if is_new else job.version
            next_version = "v1.0" if is_new else _next_version(job, db)
            job.version = next_version
            db.add(EvolutionEvent(
                job_id=job.id,
                added_skills=json.dumps(added, ensure_ascii=False),
                removed_skills="[]",
                modified_skills=json.dumps(modified, ensure_ascii=False),
                update_note=f"根据 {source_label} 真实 JD 发布岗位能力画像。",
                data_sources=json.dumps([source.source_name, *evidence_urls[:3]], ensure_ascii=False),
                confidence=confidence,
                version_record=json.dumps([previous_version, next_version], ensure_ascii=False),
                evidence=evidence_note,
                created_at=max((raw.published_at or raw.created_at for raw in raw_rows), default=datetime.utcnow()),
            ))
            evolution_events += 1

        published_parsed_ids.extend(item.id for item in parsed_rows)

    result = {
        "eligible_jd_count": len(published_parsed_ids),
        "skipped_jd_count": len(skipped),
        "skipped": skipped[:20],
        "created_jobs": created_jobs,
        "updated_jobs": updated_jobs,
        "created_skills": created_skills,
        "added_relations": added_relations,
        "upgraded_relations": upgraded_relations,
        "evolution_events": evolution_events,
        "published_at": datetime.utcnow().isoformat(),
    }
    metadata = _evidence(source.metadata_json)
    metadata["integration"] = result
    source.metadata_json = json.dumps(metadata, ensure_ascii=False)
    source.status = "published" if published_parsed_ids else "parsed_needs_review"
    source.sync_message = (
        f"已发布 {len(published_parsed_ids)} 条可信 JD：新增岗位 {created_jobs}，更新岗位 {updated_jobs}，"
        f"新增能力关系 {added_relations}，生成演化事件 {evolution_events}；跳过 {len(skipped)} 条。"
    )
    return result
