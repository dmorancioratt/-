"""Generate match predictions from the current database graph.

This intentionally replaces the old hand-authored prediction fixture.  Run it
before the offline evaluation, or let ``run_eval`` invoke it automatically.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models import JobEntity
from app.services.matching import rank_job_profiles

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "samples" / "input" / "match_candidates.jsonl"
OUTPUT_PATH = BASE_DIR / "samples" / "pred" / "match_pred.jsonl"


def _load_inputs() -> list[dict]:
    return [json.loads(line) for line in INPUT_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def _profiles(db) -> list[dict]:
    rows = db.scalars(select(JobEntity).order_by(JobEntity.id)).all()
    profiles = []
    for job in rows:
        relations = sorted(job.skill_relations, key=lambda relation: relation.weight, reverse=True)
        profiles.append(
            {
                "id": job.id,
                "name": job.name,
                "domain": job.domain,
                "level": job.level,
                "description": job.description,
                "required_skills": [relation.skill.name for relation in relations if relation.relation_type == "requires"],
                "preferred_skills": [relation.skill.name for relation in relations if relation.relation_type != "requires"],
            }
        )
    return profiles


def generate() -> list[dict]:
    with SessionLocal() as db:
        profiles = _profiles(db)
        if not profiles:
            raise RuntimeError("当前岗位图谱为空，无法生成匹配评测")
        predictions = []
        for candidate in _load_inputs():
            ranking = rank_job_profiles(candidate, profiles)
            predictions.append(
                {
                    "id": candidate["id"],
                    "top1_job": ranking[0]["job_name"],
                    "top3_jobs": [item["job_name"] for item in ranking[:3]],
                    "top1_score": ranking[0]["ranking_score"],
                    "focus_hits": ranking[0]["focus_hits"],
                    "scoring_version": ranking[0]["report"]["scoring_version"],
                }
            )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in predictions) + "\n", encoding="utf-8")
    return predictions


if __name__ == "__main__":
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
