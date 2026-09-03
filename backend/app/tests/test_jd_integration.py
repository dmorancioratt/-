from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import delete, select

from app.db.database import SessionLocal
from app.models import DataSource, EvolutionEvent, JobEntity, JobSkillRelation, ParsedJD, RawJD, SkillEntity
from app.services.jd_integration import publish_jd_batch
from app.services.jd_parser import text_hash


def test_verified_jd_batch_publishes_idempotently_to_capability_graph():
    suffix = uuid4().hex[:8]
    job_name = f"可信RAG工程师-{suffix}"
    skill_names = [f"检索增强-{suffix}", f"向量数据库-{suffix}"]
    source_id = raw_id = parsed_id = job_id = None
    try:
        with SessionLocal() as db:
            source = DataSource(
                source_key=f"jd-import-test-{suffix}",
                source_name=f"测试 JD 来源-{suffix}",
                publisher="测试机构",
                source_url="https://example.com/jobs",
                license_name="测试许可",
                version="测试版",
                data_type="真实岗位 JD",
                domain="人工智能",
                data_count=1,
                indexed_count=1,
                quality_score=95,
                status="parsed",
                metadata_json="{}",
            )
            db.add(source)
            db.flush()
            source_id = source.id
            content = f"招聘{job_name}，要求掌握{skill_names[0]}和{skill_names[1]}。"
            raw = RawJD(
                source_id=source.id,
                title=job_name,
                content=content,
                text_hash=text_hash(content),
                source_url="https://example.com/jobs/1",
                publisher="测试机构",
                parse_status="parsed",
            )
            db.add(raw)
            db.flush()
            raw_id = raw.id
            parsed = ParsedJD(
                raw_jd_id=raw.id,
                job_name=job_name,
                domain="人工智能",
                level="中级",
                responsibilities=json.dumps(["建设企业知识库"], ensure_ascii=False),
                required_skills=json.dumps([skill_names[0]], ensure_ascii=False),
                preferred_skills=json.dumps([skill_names[1]], ensure_ascii=False),
                tools="[]",
                certificates="[]",
                experience="3 年",
                scenarios="[]",
                confidence=0.94,
                evidence=json.dumps({"guard_status": "passed", "sources": [{"quote": skill_names[0]}]}, ensure_ascii=False),
            )
            db.add(parsed)
            db.commit()
            parsed_id = parsed.id

            first = publish_jd_batch(db, source.id)
            db.commit()
            assert first["eligible_jd_count"] == 1
            assert first["created_jobs"] == 1
            assert first["added_relations"] == 2
            assert first["evolution_events"] == 1

            job = db.scalar(select(JobEntity).where(JobEntity.name == job_name))
            assert job is not None
            job_id = job.id
            assert job.version == "v1.0"
            relations = db.scalars(select(JobSkillRelation).where(JobSkillRelation.job_id == job.id)).all()
            assert {relation.skill.name for relation in relations} == set(skill_names)

            second = publish_jd_batch(db, source.id)
            db.commit()
            assert second["created_jobs"] == 0
            assert second["added_relations"] == 0
            assert second["evolution_events"] == 0
            assert db.scalar(select(EvolutionEvent).where(EvolutionEvent.job_id == job.id)) is not None
    finally:
        with SessionLocal() as db:
            if job_id:
                db.execute(delete(JobSkillRelation).where(JobSkillRelation.job_id == job_id))
                db.execute(delete(EvolutionEvent).where(EvolutionEvent.job_id == job_id))
                db.execute(delete(JobEntity).where(JobEntity.id == job_id))
            if parsed_id:
                db.execute(delete(ParsedJD).where(ParsedJD.id == parsed_id))
            if raw_id:
                db.execute(delete(RawJD).where(RawJD.id == raw_id))
            db.execute(delete(SkillEntity).where(SkillEntity.name.in_(skill_names)))
            if source_id:
                db.execute(delete(DataSource).where(DataSource.id == source_id))
            db.commit()
