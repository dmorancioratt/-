"""Cross-source JD validation and source credibility scoring."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models import DataSource, RawJD


PLAGIARISM_THRESHOLD = float(os.getenv("JD_PLAGIARISM_THRESHOLD", "0.82"))
TIME_DECAY_HALF_LIFE_DAYS = max(1, int(os.getenv("JD_TIME_DECAY_HALF_LIFE_DAYS", "180")))
MAX_VALIDATION_JDS = max(100, int(os.getenv("JD_VALIDATION_MAX_JDS", "2000")))
MIN_VALID_JD_CHARS = 40
_NORMALIZE_RE = re.compile(r"[^0-9a-z\u4e00-\u9fff]+", re.IGNORECASE)
_NOISE_MARKERS = ("加微信", "刷单", "代理加盟", "高薪日结", "无门槛", "返利", "博彩")


def normalize_jd(text: str) -> str:
    return _NORMALIZE_RE.sub("", (text or "").casefold())


def _shingles(text: str, size: int = 5) -> set[str]:
    normalized = normalize_jd(text)
    if len(normalized) <= size:
        return {normalized} if normalized else set()
    return {normalized[index:index + size] for index in range(len(normalized) - size + 1)}


def _simhash(shingles: Iterable[str]) -> int:
    vector = [0] * 64
    seen = False
    for shingle in shingles:
        seen = True
        value = int.from_bytes(hashlib.blake2b(shingle.encode("utf-8"), digest_size=8).digest(), "big")
        for bit in range(64):
            vector[bit] += 1 if value & (1 << bit) else -1
    if not seen:
        return 0
    result = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            result |= 1 << bit
    return result


def plagiarism_similarity(left: str, right: str) -> float:
    left_normalized = normalize_jd(left)
    right_normalized = normalize_jd(right)
    if not left_normalized or not right_normalized:
        return 0.0
    if left_normalized == right_normalized:
        return 1.0
    left_shingles = _shingles(left)
    right_shingles = _shingles(right)
    left_hash = _simhash(left_shingles)
    right_hash = _simhash(right_shingles)
    simhash_score = 1 - ((left_hash ^ right_hash).bit_count() / 64)
    if simhash_score < 0.62:
        return round(simhash_score, 4)
    union = left_shingles | right_shingles
    jaccard = len(left_shingles & right_shingles) / len(union) if union else 0.0
    shingle_score = jaccard * 0.72 + simhash_score * 0.28
    sequence_score = SequenceMatcher(None, left_normalized, right_normalized, autojunk=False).ratio()
    return round(max(shingle_score, sequence_score), 4)


def is_noise_jd(title: str, content: str) -> tuple[bool, list[str]]:
    normalized = normalize_jd(content)
    reasons: list[str] = []
    if len(normalized) < MIN_VALID_JD_CHARS:
        reasons.append(f"正文有效字符少于 {MIN_VALID_JD_CHARS}")
    if not normalize_jd(title):
        reasons.append("岗位标题为空")
    marker_hits = [marker for marker in _NOISE_MARKERS if marker in content]
    if marker_hits:
        reasons.append(f"包含高风险推广词：{'、'.join(marker_hits[:3])}")
    if normalized:
        most_common = max(normalized.count(char) for char in set(normalized))
        if most_common / len(normalized) > 0.35:
            reasons.append("正文存在异常字符重复")
    return bool(reasons), reasons


def time_decay_weight(value: datetime | None, *, now: datetime | None = None) -> float:
    if value is None:
        return 0.5
    current = now or datetime.utcnow()
    age_days = max(0.0, (current - value).total_seconds() / 86400)
    return round(math.exp(-math.log(2) * age_days / TIME_DECAY_HALF_LIFE_DAYS), 4)


def _metadata(source: DataSource) -> dict:
    try:
        value = json.loads(source.metadata_json or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _provenance_score(source: DataSource, metadata: dict) -> float:
    checks = (
        bool(source.publisher.strip()),
        source.source_url.startswith("https://"),
        bool(source.license_name.strip()),
        bool(source.source_key.strip()),
        bool(metadata.get("verified") or metadata.get("primary_or_authoritative")),
    )
    return round(sum(checks) / len(checks), 4)


def _mutation_benchmark(rows: list[RawJD]) -> tuple[float | None, int]:
    samples = [row for row in rows if len(normalize_jd(row.content)) >= MIN_VALID_JD_CHARS][:30]
    if not samples:
        return None, 0
    recalled = 0
    for row in samples:
        source = row.content
        mutated = "".join(char for index, char in enumerate(source) if index % 53 != 0)
        mutated = re.sub(r"\d+", "2026", mutated)
        if plagiarism_similarity(source, mutated) >= PLAGIARISM_THRESHOLD:
            recalled += 1
    return round(recalled / len(samples), 4), len(samples)


def validate_source_trust(db: Session, *, now: datetime | None = None, commit: bool = True) -> dict:
    generated_at = now or datetime.utcnow()
    sources = list(db.scalars(select(DataSource).where(DataSource.status != "archived").order_by(DataSource.id)).all())
    source_by_id = {source.id: source for source in sources}
    rows = list(reversed(db.scalars(
        select(RawJD)
        .where(RawJD.source_id.is_not(None))
        .order_by(RawJD.created_at.desc(), RawJD.id.desc())
        .limit(MAX_VALIDATION_JDS)
    ).all()))

    for row in rows:
        if row.parse_status in {"filtered_noise", "filtered_duplicate"}:
            row.parse_status = "pending"
            row.parse_error = ""
        row.is_duplicate = False

    noise_reasons: dict[int, list[str]] = {}
    clean_rows: list[RawJD] = []
    for row in rows:
        noisy, reasons = is_noise_jd(row.title, row.content)
        if noisy:
            noise_reasons[row.id] = reasons
            row.parse_status = "filtered_noise"
            row.parse_error = "；".join(reasons)[:500]
        else:
            clean_rows.append(row)

    plagiarism_matches: dict[int, dict] = {}
    fingerprints: list[tuple[RawJD, int, set[str]]] = []
    for row in clean_rows:
        shingles = _shingles(row.content)
        current_hash = _simhash(shingles)
        best: tuple[RawJD, float] | None = None
        for candidate, candidate_hash, candidate_shingles in fingerprints:
            simhash_score = 1 - ((current_hash ^ candidate_hash).bit_count() / 64)
            if simhash_score < 0.62:
                continue
            union = shingles | candidate_shingles
            jaccard = len(shingles & candidate_shingles) / len(union) if union else 0.0
            shingle_score = jaccard * 0.72 + simhash_score * 0.28
            sequence_score = SequenceMatcher(
                None,
                normalize_jd(row.content),
                normalize_jd(candidate.content),
                autojunk=False,
            ).ratio()
            similarity = max(shingle_score, sequence_score)
            if similarity >= PLAGIARISM_THRESHOLD and (best is None or similarity > best[1]):
                best = (candidate, similarity)
        if best is not None:
            original, similarity = best
            row.is_duplicate = True
            row.parse_status = "filtered_duplicate"
            row.parse_error = f"近似抄袭 JD；与记录 {original.id} 相似度 {similarity:.3f}"
            plagiarism_matches[row.id] = {
                "original_id": original.id,
                "similarity": round(similarity, 4),
                "cross_source": original.source_id != row.source_id,
            }
        else:
            fingerprints.append((row, current_hash, shingles))

    benchmark_recall, benchmark_size = _mutation_benchmark(clean_rows)
    rows_by_source: dict[int, list[RawJD]] = defaultdict(list)
    for row in rows:
        if row.source_id is not None:
            rows_by_source[row.source_id].append(row)

    scored: list[tuple[DataSource, dict, float]] = []
    for source in sources:
        metadata = _metadata(source)
        source_rows = rows_by_source.get(source.id, [])
        total = len(source_rows)
        noise_count = sum(row.id in noise_reasons for row in source_rows)
        plagiarism_count = sum(row.id in plagiarism_matches for row in source_rows)
        valid_count = max(0, total - noise_count - plagiarism_count)
        if total:
            noise_rate = noise_count / total
            plagiarism_rate = plagiarism_count / total
            validity = valid_count / total
            originality = 1 - plagiarism_rate
            source.indexed_count = valid_count
            source.noise_rate = round(noise_rate, 4)
            source.duplicate_rate = round(plagiarism_rate, 4)
        else:
            noise_rate = float(source.noise_rate or 0)
            plagiarism_rate = float(source.duplicate_rate or 0)
            validity = max(0.0, 1 - noise_rate)
            originality = max(0.0, 1 - plagiarism_rate)

        valid_source_rows = [
            row for row in source_rows
            if row.id not in noise_reasons and row.id not in plagiarism_matches
        ]
        reference_date = max(
            (row.published_at or row.created_at for row in valid_source_rows),
            default=source.last_synced_at or source.published_at or source.uploaded_at,
        )
        decay = time_decay_weight(reference_date, now=generated_at)
        provenance = _provenance_score(source, metadata)
        coverage = min(1.0, (source.indexed_count or 0) / max(1, source.data_count or total or 1))
        trust_score = round(100 * (
            0.27 * provenance
            + 0.25 * validity
            + 0.20 * originality
            + 0.18 * decay
            + 0.10 * coverage
        ), 2)
        support = 0.5 + 0.5 * min(1.0, math.log1p(max(total, source.indexed_count or 0)) / math.log1p(1000))
        raw_weight = max(0.01, trust_score / 100 * support)
        validation = {
            "trust_score": trust_score,
            "weight": 0.0,
            "jd_count": total,
            "valid_jd_count": valid_count if total else source.indexed_count or 0,
            "noise_count": noise_count,
            "noise_rate": round(noise_rate, 4),
            "plagiarism_count": plagiarism_count,
            "plagiarism_rate": round(plagiarism_rate, 4),
            "time_decay_weight": decay,
            "provenance_score": provenance,
            "coverage_score": round(coverage, 4),
            "plagiarism_recall": benchmark_recall,
            "recall_sample_size": benchmark_size,
            "recall_benchmark": "mutation-v1" if benchmark_size else None,
            "validated_at": generated_at.isoformat(),
        }
        scored.append((source, validation, raw_weight))

    total_weight = sum(item[2] for item in scored) or 1.0
    report_sources: list[dict] = []
    for source, validation, raw_weight in scored:
        validation["weight"] = round(raw_weight / total_weight, 6)
        metadata = _metadata(source)
        metadata["source_validation"] = validation
        source.metadata_json = json.dumps(metadata, ensure_ascii=False)
        source.quality_score = validation["trust_score"]
        report_sources.append({
            "id": source.id,
            "source_key": source.source_key,
            "source_name": source.source_name,
            **validation,
        })

    if commit:
        db.commit()
    return {
        "generated_at": generated_at.isoformat(),
        "algorithm": {
            "version": "source-trust-v1",
            "plagiarism_threshold": PLAGIARISM_THRESHOLD,
            "time_decay_half_life_days": TIME_DECAY_HALF_LIFE_DAYS,
            "recall_benchmark": "mutation-v1",
        },
        "summary": {
            "source_count": len(sources),
            "jd_count": len(rows),
            "noise_count": len(noise_reasons),
            "plagiarism_count": len(plagiarism_matches),
            "cross_source_plagiarism_count": sum(bool(item["cross_source"]) for item in plagiarism_matches.values()),
            "plagiarism_recall": benchmark_recall,
            "recall_sample_size": benchmark_size,
        },
        "sources": report_sources,
    }


def scheduled_source_validation() -> None:
    with SessionLocal() as db:
        validate_source_trust(db)


def source_validation_report(db: Session) -> dict:
    sources = list(db.scalars(select(DataSource).where(DataSource.status != "archived").order_by(DataSource.id)).all())
    rows: list[dict] = []
    generated_at: str | None = None
    for source in sources:
        validation = _metadata(source).get("source_validation")
        if not isinstance(validation, dict):
            continue
        generated_at = max(generated_at or "", str(validation.get("validated_at") or "")) or generated_at
        rows.append({
            "id": source.id,
            "source_key": source.source_key,
            "source_name": source.source_name,
            **validation,
        })
    recall_rows = [row for row in rows if row.get("plagiarism_recall") is not None]
    return {
        "generated_at": generated_at,
        "algorithm": {
            "version": "source-trust-v1",
            "plagiarism_threshold": PLAGIARISM_THRESHOLD,
            "time_decay_half_life_days": TIME_DECAY_HALF_LIFE_DAYS,
            "recall_benchmark": "mutation-v1",
        },
        "summary": {
            "source_count": len(rows),
            "jd_count": sum(int(row.get("jd_count") or 0) for row in rows),
            "noise_count": sum(int(row.get("noise_count") or 0) for row in rows),
            "plagiarism_count": sum(int(row.get("plagiarism_count") or 0) for row in rows),
            "plagiarism_recall": recall_rows[0].get("plagiarism_recall") if recall_rows else None,
            "recall_sample_size": recall_rows[0].get("recall_sample_size") if recall_rows else 0,
        },
        "sources": rows,
    }
