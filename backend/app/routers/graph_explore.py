"""图谱探索与能力演化模块。

该模块把 jobgraph 项目的「知识图谱探索」和「能力演化分析」能力融合进数融智联，
直接基于现有 SQLite 中的岗位、技能、岗位-技能关系和能力更新事件计算，
不依赖外部图数据库，作为一个自包含的可插拔模块提供以下接口：

- GET /api/graph/full        全图数据（含社区着色、中心度、节点大小）
- GET /api/graph/stats       图谱统计概览（节点/关系/社区/平均度/核心枢纽）
- GET /api/graph/communities 社区分布（按岗位领域聚类）
- GET /api/graph/path        两个岗位之间的技能迁移最短路径
- GET /api/graph/search      岗位/技能搜索
- GET /api/evolution/timeline 能力演化时间线（新增/删除/修改技能随时间变化）
- GET /api/evolution/hotspot  能力热点（上升/下降技能）
- GET /api/evolution/compare  领域能力对比
"""

import ast
import json
from collections import defaultdict, deque
from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import DataSource, EvolutionEvent, ExternalCatalogItem, JobEntity, JobSkillRelation, RawJD, SkillEntity

router = APIRouter(prefix="/api", tags=["graph-explore"])

# 社区配色使用低饱和冷色谱，和深蓝玻璃拟态背景保持一致。
COMMUNITY_PALETTE = [
    "#5B9BD5",
    "#53B7C2",
    "#748ED1",
    "#5EA6BA",
    "#64B8A3",
    "#8299C9",
    "#5AACA7",
    "#8BA7D2",
    "#6794C2",
    "#74B6C9",
]


def _parse_list(value) -> list:
    """把种子数据里的字段解析成列表，兼容 "['a','b']"、含字典的列表以及 "a,b" 逗号串。"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, list) else [parsed]
    except (SyntaxError, ValueError):
        return [item.strip() for item in text.strip("[]").split(",") if item.strip()]


def _skill_names(value) -> list[str]:
    """把技能列表统一成名称字符串，兼容 [{'skill': 'Redis', 'change': ...}] 这类结构。"""
    names = []
    for item in _parse_list(value):
        if isinstance(item, dict):
            name = item.get("skill") or item.get("name")
            if name:
                names.append(str(name))
        elif item:
            names.append(str(item))
    return names


def _modified_skill_items(value) -> list[dict]:
    items = []
    for item in _parse_list(value):
        if isinstance(item, dict):
            name = item.get("skill") or item.get("name")
            if name:
                items.append({"name": str(name), "change": str(item.get("change") or "")})
        elif item:
            items.append({"name": str(item), "change": ""})
    return items


def _event_month(value: datetime | None) -> str:
    return value.strftime("%Y-%m") if value else "未知"


def _job_skill_names(job_id: int, rels_by_job: dict[int, list[JobSkillRelation]], skills: dict[int, SkillEntity], limit: int = 16) -> list[str]:
    rels = sorted(rels_by_job.get(job_id, []), key=lambda rel: float(rel.weight or 0), reverse=True)
    names = []
    for rel in rels:
        skill = skills.get(rel.skill_id)
        if skill and skill.name not in names:
            names.append(skill.name)
        if len(names) >= limit:
            break
    return names


def _source_signal_skills(items: list[ExternalCatalogItem], fallback: list[str], limit: int = 8) -> list[str]:
    def sort_key(item: ExternalCatalogItem):
        payload = {}
        try:
            payload = json.loads(item.payload_json or "{}")
        except (TypeError, json.JSONDecodeError):
            payload = {}
        rank = payload.get("rank")
        importance = payload.get("importance")
        hot = bool(payload.get("hot_technology") or payload.get("in_demand"))
        return (0 if hot else 1, int(rank or 9999), -float(importance or 0), item.name)

    names = []
    for source_group in (
        sorted([row for row in items if row.item_type in {"skill", "essential_skill"}], key=sort_key),
        fallback,
        sorted([row for row in items if row.item_type == "software_skill"], key=sort_key),
    ):
        for item in source_group:
            name = item.name if isinstance(item, ExternalCatalogItem) else str(item)
            if name and name not in names:
                names.append(name)
            if len(names) >= limit:
                return names
    return names


def _canonical_evolution_events(db: Session) -> list[dict]:
    """Return real version events, or derive a timeline from versioned source data when no events were recorded."""
    jobs = {job.id: job for job in db.scalars(select(JobEntity)).all()}
    persisted = db.scalars(select(EvolutionEvent).order_by(EvolutionEvent.created_at)).all()
    if persisted:
        detail = []
        for event in persisted:
            job = jobs.get(event.job_id)
            versions = _skill_names(event.version_record)
            detail.append(
                {
                    "jobId": event.job_id,
                    "jobName": job.name if job else f"岗位#{event.job_id}",
                    "domain": job.domain if job else "其他",
                    "date": _event_month(event.created_at),
                    "createdAt": event.created_at,
                    "added": _skill_names(event.added_skills),
                    "removed": _skill_names(event.removed_skills),
                    "modified": _modified_skill_items(event.modified_skills),
                    "note": event.update_note or "",
                    "confidence": round(float(event.confidence or 0), 2),
                    "version": versions[-1] if versions else "",
                    "fromVersion": versions[0] if versions else "v1.0",
                    "toVersion": versions[-1] if len(versions) > 1 else (versions[0] if versions else "v1.1"),
                    "evidence": event.evidence or "",
                    "dataSources": _skill_names(event.data_sources),
                    "derived": False,
                }
            )
        return detail

    return _derive_evolution_from_sources(db, jobs)


def _derive_evolution_from_sources(db: Session, jobs: dict[int, JobEntity]) -> list[dict]:
    sources = db.scalars(
        select(DataSource)
        .where(DataSource.status != "archived")
        .order_by(DataSource.published_at, DataSource.uploaded_at, DataSource.id)
    ).all()
    if not sources or not jobs:
        return []

    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    relations = db.scalars(select(JobSkillRelation)).all()
    rels_by_job: dict[int, list[JobSkillRelation]] = defaultdict(list)
    for rel in relations:
        rels_by_job[rel.job_id].append(rel)

    source_keys = [source.source_key for source in sources if source.source_key]
    external_items = db.scalars(
        select(ExternalCatalogItem).where(ExternalCatalogItem.source_key.in_(source_keys))
    ).all() if source_keys else []
    items_by_source: dict[str, list[ExternalCatalogItem]] = defaultdict(list)
    for item in external_items:
        items_by_source[item.source_key].append(item)

    jobs_by_domain: dict[str, list[JobEntity]] = defaultdict(list)
    for job in jobs.values():
        jobs_by_domain[job.domain or "其他"].append(job)
    all_jobs = sorted(jobs.values(), key=lambda job: (job.domain or "", job.name))

    cumulative: set[str] = set()
    detail: list[dict] = []
    for idx, source in enumerate(sources):
        domain_jobs = jobs_by_domain.get(source.domain or "", [])
        target_pool = domain_jobs or all_jobs
        if not target_pool:
            continue
        job = target_pool[idx % len(target_pool)]
        current = _job_skill_names(job.id, rels_by_job, skills, limit=20)
        signals = _source_signal_skills(items_by_source.get(source.source_key, []), current, limit=8)
        if not signals and not current:
            continue

        added = [name for name in signals if name not in cumulative][:4]
        if not added:
            added = [name for name in current if name not in cumulative][:3] or signals[:3]

        removed: list[str] = []
        if idx > 0:
            signal_set = set(signals)
            added_set = set(added)
            removed = [
                name for name in reversed(current)
                if name not in signal_set and name not in added_set
            ][:1]

        modified_names = [name for name in signals if name in cumulative and name not in removed][:2]
        if not modified_names and idx > 0 and signals:
            modified_names = signals[:1]
        modified = [
            {"name": name, "change": f"随 {source.source_name} 更新为当前阶段重点能力"}
            for name in modified_names
        ]

        published_at = source.published_at or source.uploaded_at
        date_key = _event_month(published_at)
        version = source.version or date_key
        confidence = round(min(0.96, max(0.68, float(source.quality_score or 82) / 100)), 2)
        detail.append(
            {
                "jobId": job.id,
                "jobName": job.name,
                "domain": job.domain or source.domain or "其他",
                "date": date_key,
                "createdAt": published_at,
                "added": added,
                "removed": removed,
                "modified": modified,
                "note": f"根据「{source.source_name}」{version} 数据推导 {job.name} 能力画像迭代。",
                "confidence": confidence,
                "version": version,
                "fromVersion": f"T{idx + 1:02d}",
                "toVersion": f"T{idx + 2:02d}",
                "evidence": source.sync_message or f"数据源 {source.source_key or source.source_name}，记录量 {source.data_count or 0}，索引 {source.indexed_count or 0}。",
                "dataSources": [source.source_name],
                "derived": True,
            }
        )
        cumulative.update(added)
        cumulative.update(signals[:4])
    return detail


def _build_graph(db: Session):
    """从数据库构建图结构，并计算社区、度数、中心度。返回一个上下文字典。"""
    jobs = db.scalars(select(JobEntity)).all()
    skills = db.scalars(select(SkillEntity)).all()
    relations = db.scalars(select(JobSkillRelation)).all()

    # 1) 社区 = 岗位领域(domain)。为每个领域分配稳定的索引与颜色。
    domains = sorted({(job.domain or "其他") for job in jobs})
    domain_index = {domain: idx for idx, domain in enumerate(domains)}

    skill_by_id = {skill.id: skill for skill in skills}
    job_by_id = {job.id: job for job in jobs}

    # 2) 技能归属社区：归到与它连接权重最大的岗位所属领域。
    skill_domain_weight: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    degree: dict[str, int] = defaultdict(int)
    adjacency: dict[str, set] = defaultdict(set)
    edges = []

    for rel in relations:
        job = job_by_id.get(rel.job_id)
        skill = skill_by_id.get(rel.skill_id)
        if not job or not skill:
            continue
        job_node = f"job-{job.id}"
        skill_node = f"skill-{skill.id}"
        weight = float(rel.weight or 1)
        skill_domain_weight[skill.id][job.domain or "其他"] += weight
        degree[job_node] += 1
        degree[skill_node] += 1
        adjacency[job_node].add(skill_node)
        adjacency[skill_node].add(job_node)
        edges.append(
            {
                "source": job_node,
                "target": skill_node,
                "weight": round(weight, 2),
                "relation": rel.relation_type or "requires",
                "evidence": rel.evidence or "",
            }
        )

    skill_community: dict[int, int] = {}
    for skill in skills:
        weights = skill_domain_weight.get(skill.id)
        if weights:
            best_domain = max(weights.items(), key=lambda kv: kv[1])[0]
        else:
            best_domain = domains[0] if domains else "其他"
        skill_community[skill.id] = domain_index.get(best_domain, 0)

    max_degree = max(degree.values()) if degree else 1

    return {
        "jobs": jobs,
        "skills": skills,
        "edges": edges,
        "domains": domains,
        "domain_index": domain_index,
        "skill_community": skill_community,
        "degree": degree,
        "adjacency": adjacency,
        "max_degree": max_degree,
    }


def _job_node(job, ctx) -> dict:
    node_id = f"job-{job.id}"
    deg = ctx["degree"].get(node_id, 0)
    community = ctx["domain_index"].get(job.domain or "其他", 0)
    return {
        "id": node_id,
        "label": job.name,
        "type": "job",
        "community": community,
        "communityName": job.domain or "其他",
        "color": COMMUNITY_PALETTE[community % len(COMMUNITY_PALETTE)],
        "degree": deg,
        "centrality": round(deg / ctx["max_degree"], 2),
        "level": job.level,
        "isEmerging": bool(job.is_emerging),
        "size": round(26 + deg * 2.2, 1),
        "evidence": job.evidence or "",
    }


def _skill_node(skill, ctx) -> dict:
    node_id = f"skill-{skill.id}"
    deg = ctx["degree"].get(node_id, 0)
    community = ctx["skill_community"].get(skill.id, 0)
    return {
        "id": node_id,
        "label": skill.name,
        "type": "skill",
        "community": community,
        "communityName": ctx["domains"][community] if ctx["domains"] else "其他",
        "color": COMMUNITY_PALETTE[community % len(COMMUNITY_PALETTE)],
        "category": skill.category,
        "degree": deg,
        "centrality": round(deg / ctx["max_degree"], 2),
        "size": round(14 + deg * 1.8, 1),
        "evidence": skill.evidence or "",
    }


@router.get("/graph/full")
def graph_full(
    keyword: str = Query(default=""),
    community: int | None = Query(default=None),
    limit: int = Query(default=320, ge=20, le=1000),
    db: Session = Depends(get_db),
):
    ctx = _build_graph(db)
    nodes = [_job_node(job, ctx) for job in ctx["jobs"]]
    nodes += [_skill_node(skill, ctx) for skill in ctx["skills"]]

    kw = keyword.strip().lower()
    if kw:
        nodes = [n for n in nodes if kw in n["label"].lower()]
    if community is not None:
        nodes = [n for n in nodes if n["community"] == community]

    # 优先保留度数高的节点
    nodes.sort(key=lambda n: n["degree"], reverse=True)
    nodes = nodes[:limit]
    node_ids = {n["id"] for n in nodes}
    edges = [e for e in ctx["edges"] if e["source"] in node_ids and e["target"] in node_ids]

    return {
        "nodes": nodes,
        "edges": edges,
        "communities": _community_payload(ctx),
        "stats": _stats_payload(ctx),
    }


def _community_payload(ctx) -> list:
    job_count = defaultdict(int)
    skill_count = defaultdict(int)
    for job in ctx["jobs"]:
        job_count[ctx["domain_index"].get(job.domain or "其他", 0)] += 1
    for skill in ctx["skills"]:
        skill_count[ctx["skill_community"].get(skill.id, 0)] += 1
    result = []
    for domain, idx in sorted(ctx["domain_index"].items(), key=lambda kv: kv[1]):
        result.append(
            {
                "index": idx,
                "name": domain,
                "color": COMMUNITY_PALETTE[idx % len(COMMUNITY_PALETTE)],
                "jobCount": job_count.get(idx, 0),
                "skillCount": skill_count.get(idx, 0),
                "count": job_count.get(idx, 0) + skill_count.get(idx, 0),
            }
        )
    result.sort(key=lambda c: c["count"], reverse=True)
    return result


def _stats_payload(ctx) -> dict:
    node_count = len(ctx["jobs"]) + len(ctx["skills"])
    edge_count = len(ctx["edges"])
    top_hubs = sorted(
        (
            {
                "label": job.name,
                "type": "job",
                "degree": ctx["degree"].get(f"job-{job.id}", 0),
            }
            for job in ctx["jobs"]
        ),
        key=lambda h: h["degree"],
        reverse=True,
    )[:6]
    return {
        "nodeCount": node_count,
        "jobCount": len(ctx["jobs"]),
        "skillCount": len(ctx["skills"]),
        "edgeCount": edge_count,
        "communityCount": len(ctx["domains"]),
        "avgDegree": round(edge_count * 2 / node_count, 2) if node_count else 0,
        "topHubs": top_hubs,
    }


@router.get("/graph/stats")
def graph_stats(db: Session = Depends(get_db)):
    return _stats_payload(_build_graph(db))


@router.get("/graph/communities")
def graph_communities(db: Session = Depends(get_db)):
    return _community_payload(_build_graph(db))


@router.get("/graph/path")
def graph_path(
    from_job: int = Query(...),
    to_job: int = Query(...),
    db: Session = Depends(get_db),
):
    """在岗位-技能二部图上做 BFS，找出两个岗位之间的技能迁移路径。"""
    ctx = _build_graph(db)
    start = f"job-{from_job}"
    goal = f"job-{to_job}"
    adjacency = ctx["adjacency"]
    if start not in adjacency or goal not in adjacency:
        return {"found": False, "path": [], "shared": []}

    prev = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for neighbor in adjacency[current]:
            if neighbor not in prev:
                prev[neighbor] = current
                queue.append(neighbor)

    if goal not in prev:
        return {"found": False, "path": [], "shared": []}

    chain = []
    cursor = goal
    while cursor is not None:
        chain.append(cursor)
        cursor = prev[cursor]
    chain.reverse()

    job_by_id = {f"job-{job.id}": job for job in ctx["jobs"]}
    skill_by_id = {f"skill-{skill.id}": skill for skill in ctx["skills"]}
    path = []
    for node_id in chain:
        if node_id in job_by_id:
            path.append({"id": node_id, "label": job_by_id[node_id].name, "type": "job"})
        elif node_id in skill_by_id:
            path.append({"id": node_id, "label": skill_by_id[node_id].name, "type": "skill"})

    # 两个岗位共享的技能（可直接迁移的能力）
    from_skills = adjacency.get(start, set())
    to_skills = adjacency.get(goal, set())
    shared = [
        skill_by_id[s].name
        for s in (from_skills & to_skills)
        if s in skill_by_id
    ]

    return {"found": True, "path": path, "shared": shared}


@router.get("/graph/search")
def graph_search(keyword: str = Query(default=""), db: Session = Depends(get_db)):
    ctx = _build_graph(db)
    kw = keyword.strip().lower()
    nodes = [_job_node(job, ctx) for job in ctx["jobs"]]
    nodes += [_skill_node(skill, ctx) for skill in ctx["skills"]]
    if kw:
        nodes = [n for n in nodes if kw in n["label"].lower()]
    nodes.sort(key=lambda n: n["degree"], reverse=True)
    return nodes[:30]


# ---------------------------------------------------------------------------
# 能力演化分析
# ---------------------------------------------------------------------------


@router.get("/evolution/timeline")
def evolution_timeline(db: Session = Depends(get_db)):
    """按时间聚合能力更新事件，展示新增/删除/修改技能的数量变化。"""
    events = _canonical_evolution_events(db)
    buckets: dict[str, dict] = {}
    detail = []
    for event in events:
        date_key = event["date"]
        bucket = buckets.setdefault(date_key, {"date": date_key, "added": 0, "removed": 0, "modified": 0, "events": 0})
        added = event["added"]
        removed = event["removed"]
        modified = event["modified"]
        bucket["added"] += len(added)
        bucket["removed"] += len(removed)
        bucket["modified"] += len(modified)
        bucket["events"] += 1
        detail.append(
            {
                "jobId": event["jobId"],
                "jobName": event["jobName"],
                "date": date_key,
                "added": added,
                "removed": removed,
                "modified": modified,
                "note": event["note"],
                "confidence": event["confidence"],
                "version": event["version"],
                "evidence": event["evidence"],
                "dataSources": event["dataSources"],
                "derived": event["derived"],
            }
        )
    timeline = sorted(buckets.values(), key=lambda b: b["date"])
    return {"timeline": timeline, "events": detail, "total": len(events), "derived": bool(events and all(e["derived"] for e in events))}


@router.get("/evolution/hotspot")
def evolution_hotspot(db: Session = Depends(get_db)):
    """能力热点：结合岗位需求量与演化事件中的新增/删除频次，给出上升与下降技能。"""
    relations = db.scalars(select(JobSkillRelation)).all()
    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    events = _canonical_evolution_events(db)

    demand = defaultdict(int)
    weight_sum = defaultdict(float)
    for rel in relations:
        demand[rel.skill_id] += 1
        weight_sum[rel.skill_id] += float(rel.weight or 1)

    added_count = defaultdict(int)
    removed_count = defaultdict(int)
    for event in events:
        for name in event["added"]:
            added_count[name] += 1
        for name in event["removed"]:
            removed_count[name] += 1

    rising = []
    for skill_id, count in demand.items():
        skill = skills.get(skill_id)
        if not skill:
            continue
        growth = added_count.get(skill.name, 0)
        heat = round(count * 0.6 + weight_sum[skill_id] * 0.2 + growth * 3, 2)
        rising.append(
            {
                "name": skill.name,
                "category": skill.category,
                "demand": count,
                "growth": growth,
                "heat": heat,
            }
        )
    rising.sort(key=lambda s: s["heat"], reverse=True)

    declining = [
        {"name": name, "removed": count}
        for name, count in sorted(removed_count.items(), key=lambda kv: kv[1], reverse=True)
    ]

    emerging = [
        {"name": name, "growth": count}
        for name, count in sorted(added_count.items(), key=lambda kv: kv[1], reverse=True)
        if name not in {skills[s].name for s in demand}
    ][:8]

    return {"rising": rising[:12], "declining": declining[:8], "emerging": emerging}


@router.get("/evolution/compare")
def evolution_compare(db: Session = Depends(get_db)):
    """按岗位领域对比能力结构：每个领域的技能类别分布与热门技能。"""
    jobs = {job.id: job for job in db.scalars(select(JobEntity)).all()}
    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    relations = db.scalars(select(JobSkillRelation)).all()

    domain_category = defaultdict(lambda: defaultdict(int))
    domain_skill = defaultdict(lambda: defaultdict(float))
    for rel in relations:
        job = jobs.get(rel.job_id)
        skill = skills.get(rel.skill_id)
        if not job or not skill:
            continue
        domain = job.domain or "其他"
        domain_category[domain][skill.category or "其他"] += 1
        domain_skill[domain][skill.name] += float(rel.weight or 1)

    categories = sorted({skill.category or "其他" for skill in skills.values()})
    domains = sorted(domain_category.keys())
    matrix = []
    for domain in domains:
        row = {"domain": domain, "categories": {cat: domain_category[domain].get(cat, 0) for cat in categories}}
        top = sorted(domain_skill[domain].items(), key=lambda kv: kv[1], reverse=True)[:6]
        row["topSkills"] = [{"name": name, "weight": round(w, 2)} for name, w in top]
        matrix.append(row)

    return {"categories": categories, "domains": domains, "matrix": matrix}


# ---------------------------------------------------------------------------
# 证据链（借鉴挑战杯国奖项目的「可解释、可追溯」表达）
# ---------------------------------------------------------------------------


def _jd_snippets(db: Session, term: str, limit: int = 5) -> list[dict]:
    """在真实 JD 正文中检索包含该词的片段，作为证据来源（不编造）。"""
    term = (term or "").strip()
    if not term:
        return []
    rows = db.scalars(select(RawJD).where(RawJD.content.like(f"%{term}%")).limit(limit)).all()
    snippets = []
    for jd in rows:
        content = jd.content or ""
        idx = content.find(term)
        start = max(0, idx - 34)
        end = min(len(content), idx + len(term) + 46)
        snippet = content[start:end].replace("\n", " ").strip()
        if start > 0:
            snippet = "…" + snippet
        if end < len(content):
            snippet = snippet + "…"
        snippets.append(
            {
                "sourceType": "jd",
                "sourceId": f"jd_{jd.id}",
                "title": jd.title,
                "snippet": snippet,
            }
        )
    return snippets


@router.get("/graph/evidence")
def graph_evidence(
    node_type: str = Query(..., pattern="^(job|skill)$"),
    node_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """节点证据链：证据说明 + 真实 JD 来源片段 + 来源数量 + 置信度 + 审核状态。"""
    if node_type == "job":
        job = db.scalar(select(JobEntity).where(JobEntity.id == node_id))
        if not job:
            raise HTTPException(status_code=404, detail="岗位不存在")
        rel_count = db.scalar(select(func.count(JobSkillRelation.id)).where(JobSkillRelation.job_id == node_id)) or 0
        sources = _jd_snippets(db, job.name)
        jd_hits = db.scalar(select(func.count(RawJD.id)).where(RawJD.content.like(f"%{job.name}%"))) or 0
        return {
            "name": job.name,
            "type": "job",
            "category": job.domain,
            "evidence": job.evidence or "",
            "confidence": 0.9 if not job.is_emerging else 0.72,
            "relationCount": rel_count,
            "sourceCount": jd_hits,
            "reviewStatus": "watching" if job.is_emerging else "approved",
            "sources": sources,
        }
    skill = db.scalar(select(SkillEntity).where(SkillEntity.id == node_id))
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    rels = db.scalars(select(JobSkillRelation).where(JobSkillRelation.skill_id == node_id)).all()
    demand = len(rels)
    avg_weight = round(sum(float(r.weight or 1) for r in rels) / demand, 2) if demand else 0.0
    sources = _jd_snippets(db, skill.name)
    jd_hits = db.scalar(select(func.count(RawJD.id)).where(RawJD.content.like(f"%{skill.name}%"))) or 0
    return {
        "name": skill.name,
        "type": "skill",
        "category": skill.category,
        "evidence": skill.evidence or "",
        "confidence": avg_weight,
        "demand": demand,
        "sourceCount": jd_hits,
        "reviewStatus": "approved" if avg_weight >= 0.6 else "needs_review",
        "sources": sources,
    }


@router.get("/evolution/version-compare")
def evolution_version_compare(db: Session = Depends(get_db)):
    """岗位能力版本对比卡：由能力更新事件重建「上一版 vs 当前版」的能力差异。"""
    events = sorted(_canonical_evolution_events(db), key=lambda item: item["createdAt"] or datetime.min, reverse=True)
    skills_by_id = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    rels_by_job: dict[int, list[JobSkillRelation]] = defaultdict(list)
    for rel in db.scalars(select(JobSkillRelation)).all():
        rels_by_job[rel.job_id].append(rel)
    cards = []
    for event in events:
        current = _job_skill_names(event["jobId"], rels_by_job, skills_by_id)
        added = event["added"]
        removed = event["removed"]
        modified = event["modified"]
        added_set = set(added)
        # 重建上一版能力集合：当前 - 本次新增 + 本次删除
        previous = [s for s in current if s not in added_set] + [s for s in removed if s not in current]
        cards.append(
            {
                "jobId": event["jobId"],
                "jobName": event["jobName"],
                "domain": event["domain"],
                "date": event["date"],
                "createdAt": event["createdAt"],
                "fromVersion": event["fromVersion"],
                "toVersion": event["toVersion"],
                "added": added,
                "removed": removed,
                "modified": modified,
                "currentSkills": current[:16],
                "previousSkills": previous[:16],
                "note": event["note"],
                "confidence": event["confidence"],
                "evidence": event["evidence"],
                "dataSources": event["dataSources"],
                "derived": event["derived"],
            }
        )
    return {"cards": cards, "total": len(cards)}


@router.get("/evaluation/report")
def evaluation_report():
    """可复现评测报告：页面实时运行核心评测，返回指标与错误案例。"""
    from app.evaluation.run_eval import run_core as run_evaluation

    try:
        results = run_evaluation()
        return {
            "command": "python -m app.evaluation.run_eval",
            "taskCount": len(results),
            "totalSamples": sum(r.samples for r in results),
            "results": [asdict(r) for r in results],
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - degrade to empty report
        return {
            "command": "python -m app.evaluation.run_eval",
            "taskCount": 0,
            "totalSamples": 0,
            "results": [],
            "error": f"评测脚本执行失败: {exc}",
        }
