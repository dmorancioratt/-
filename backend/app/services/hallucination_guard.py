from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import SystemSetting


MIN_CONFIDENCE = 0.72


@dataclass(frozen=True)
class GovernanceRules:
    evidence_required: bool = True
    low_confidence_review: bool = True
    version_history: bool = True
    confidence_threshold: float = MIN_CONFIDENCE


def get_governance_rules(db: Session) -> GovernanceRules:
    row = db.get(SystemSetting, 1)
    if row is None:
        row = SystemSetting(id=1)
        db.add(row)
        db.flush()
    return GovernanceRules(
        evidence_required=bool(row.evidence_required),
        low_confidence_review=bool(row.low_confidence_review),
        version_history=bool(row.version_history),
        confidence_threshold=float(row.confidence_threshold),
    )


def guard_payload(payload: dict, rules: GovernanceRules | None = None) -> tuple[bool, list[str]]:
    rules = rules or GovernanceRules()
    issues: list[str] = []
    if rules.evidence_required and not payload.get("evidence"):
        issues.append("缺少 evidence 字段")
    if rules.low_confidence_review and payload.get("confidence", 1) < rules.confidence_threshold:
        issues.append("置信度低于阈值")
    return len(issues) == 0, issues


def require_evidence(item: dict, default_source: str) -> dict:
    if not item.get("evidence"):
        item["evidence"] = []
        item["evidence_missing"] = True
    return item
