import re
from typing import Any


DIMENSION_WEIGHTS = {
    "required_skill_score": 0.40,
    "preferred_skill_score": 0.15,
    "project_score": 0.20,
    "tool_score": 0.10,
    "scenario_score": 0.10,
    "certificate_score": 0.05,
}

SKILL_ALIAS_GROUPS = {
    "javascript": {"javascript", "js", "ecmascript"},
    "typescript": {"typescript", "ts"},
    "vue": {"vue", "vuejs", "vue.js", "vue3"},
    "react": {"react", "reactjs", "react.js"},
    "node.js": {"node", "nodejs", "node.js"},
    "python": {"python", "py"},
    "java": {"java", "jdk"},
    "spring boot": {"springboot", "spring boot"},
    "sql": {"sql", "结构化查询语言"},
    "mysql": {"mysql"},
    "postgresql": {"postgres", "postgresql"},
    "机器学习": {"机器学习", "machine learning", "ml"},
    "深度学习": {"深度学习", "deep learning", "dl"},
    "自然语言处理": {"自然语言处理", "nlp"},
    "大语言模型": {"大语言模型", "大模型", "llm", "llms"},
    "rag": {"rag", "检索增强生成", "retrieval augmented generation"},
    "prompt engineering": {"prompt engineering", "提示词工程", "提示工程"},
    "知识图谱": {"知识图谱", "knowledge graph"},
    "docker": {"docker", "容器化"},
    "kubernetes": {"kubernetes", "k8s"},
    "git": {"git", "版本控制"},
    "linux": {"linux"},
    "ci/cd": {"ci/cd", "cicd", "持续集成", "持续交付"},
    "restful api": {"restful api", "rest api", "api开发"},
    "数据可视化": {"数据可视化", "可视化"},
    "项目管理": {"项目管理", "project management"},
}

TOOL_SKILLS = {
    "docker", "kubernetes", "git", "linux", "ci/cd", "mysql", "postgresql",
    "redis", "nginx", "prometheus", "grafana", "jenkins", "tableau", "power bi",
    "echarts", "hive", "spark", "flink", "kafka", "airflow",
}

JOB_FOCUS_TERMS = (
    "大模型", "智能体", "数据分析", "数据治理", "机器学习", "算法", "java", "前端",
    "devops", "sre", "运维", "云计算", "网络安全", "物联网", "产品经理", "ui/ux",
)

_ALIAS_LOOKUP = {
    re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", alias.lower()): canonical
    for canonical, aliases in SKILL_ALIAS_GROUPS.items()
    for alias in aliases | {canonical}
}


def score_match(
    resume_skills: list[Any],
    required: list[str],
    preferred: list[str],
    certificates: list[Any] | None = None,
    *,
    projects: list[Any] | None = None,
    internships: list[Any] | None = None,
    awards: list[Any] | None = None,
    education: str = "",
    major: str = "",
    self_summary: str = "",
    job_name: str = "",
    job_description: str = "",
    job_domain: str = "",
    job_level: str = "",
    required_weights: dict[str, float] | None = None,
    preferred_weights: dict[str, float] | None = None,
    recommended_certificates: list[str] | None = None,
) -> dict:
    """Build an explainable deterministic match report.

    AI is deliberately not allowed to invent the numeric score.  This function
    derives every dimension from candidate/job evidence; an LLM can then explain
    and extend the result without silently changing it.
    """

    certificates = certificates or []
    projects = projects or []
    internships = internships or []
    awards = awards or []
    skill_rows = [_skill_row(item) for item in resume_skills]
    skill_rows = [item for item in skill_rows if item[0]]
    explicit_skills = {canonical_skill(name): {"name": name, "level": level, "evidence": evidence} for name, level, evidence in skill_rows}

    experience_sources = _experience_sources(projects, internships, self_summary)
    all_candidate_text = "\n".join(source["text"] for source in experience_sources)
    required_eval = _evaluate_skill_group(required, explicit_skills, all_candidate_text, required_weights)
    preferred_eval = _evaluate_skill_group(preferred, explicit_skills, all_candidate_text, preferred_weights)

    project_score, project_detail = _project_score(projects, internships, required + preferred)
    tool_score, tool_detail = _tool_score(required + preferred, explicit_skills, all_candidate_text)
    scenario_score, scenario_detail = _scenario_score(
        projects,
        internships,
        self_summary,
        required + preferred,
        job_name,
        job_description,
        job_domain,
    )
    recommended_certificates = recommended_certificates or []
    certificate_score, certificate_detail = _certificate_score(
        certificates,
        awards,
        job_description,
        required + preferred,
        recommended_certificates,
    )

    scores = {
        "required_skill_score": required_eval["score"],
        "preferred_skill_score": preferred_eval["score"],
        "project_score": project_score,
        "tool_score": tool_score,
        "scenario_score": scenario_score,
        "certificate_score": certificate_score,
    }
    total = round(sum(scores[key] * weight for key, weight in DIMENSION_WEIGHTS.items()), 1)
    confidence = _confidence_score(
        bool(skill_rows), bool(projects), bool(internships), bool(certificates or awards), bool(required), bool(job_description)
    )

    matched_required = required_eval["matched"]
    matched_preferred = preferred_eval["matched"]
    missing_required = required_eval["missing"]
    missing_preferred = preferred_eval["missing"]
    suggestions = _build_suggestions(missing_required, missing_preferred, project_score, scenario_score, certificates)
    if certificate_detail.get("missing"):
        suggestions.append(
            f"可选提升项：了解{'、'.join(certificate_detail['missing'][:2])}；它们是岗位相关证明，不是强制门槛"
        )
        suggestions = _unique(suggestions)[:6]

    dimensions = [
        _dimension("必备技能", scores["required_skill_score"], 40, required_eval),
        _dimension("加分技能", scores["preferred_skill_score"], 15, preferred_eval),
        _dimension("项目经验", project_score, 20, project_detail),
        _dimension("工具平台", tool_score, 10, tool_detail),
        _dimension("行业场景", scenario_score, 10, scenario_detail),
        _dimension("证书成果", certificate_score, 5, certificate_detail),
    ]

    return {
        "total_score": total,
        **scores,
        "dimension_rows": dimensions,
        "matched_skills": _unique(matched_required + matched_preferred),
        "matched_required_skills": matched_required,
        "matched_preferred_skills": matched_preferred,
        "missing_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "matched_certificates": certificate_detail.get("matched", []),
        "missing_certificates": certificate_detail.get("missing", []),
        "recommended_certificates": recommended_certificates,
        "suggestions": suggestions,
        "confidence": confidence,
        "confidence_label": "高" if confidence >= 80 else "中" if confidence >= 55 else "低",
        "data_quality": {
            "candidate_skill_count": len(skill_rows),
            "project_count": len(projects),
            "internship_count": len(internships),
            "certificate_count": len(certificates),
            "award_count": len(awards),
            "education": education,
            "major": major,
            "job_requirement_count": len(required) + len(preferred),
            "job_certificate_count": len(recommended_certificates),
            "job_level": job_level,
        },
        "scoring_version": "evidence-v2",
        "score_weights": {dimension["name"]: dimension["weight"] for dimension in dimensions},
    }


def ratio_score(candidate: set[str], target: set[str]) -> float:
    if not target:
        return 100
    normalized_candidate = {canonical_skill(item) for item in candidate}
    normalized_target = {canonical_skill(item) for item in target}
    return round(len(normalized_candidate & normalized_target) / len(normalized_target) * 100, 1)


def rank_job_profiles(candidate: dict[str, Any], job_profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank current graph jobs using the same evidence scorer as match analysis.

    The returned ranking is deterministic and keeps the component scores so an
    evaluation report can explain why a job won instead of relying on an LLM
    or a hand-authored prediction file.
    """
    ranked: list[dict[str, Any]] = []
    candidate_text = " ".join(
        [
            *[str(_skill_row(item)[0]) for item in candidate.get("skills", [])],
            *[_item_text(item) for item in candidate.get("projects", [])],
            *[_item_text(item) for item in candidate.get("internships", [])],
            str(candidate.get("self_summary") or ""),
            str(candidate.get("target_role") or ""),
        ]
    ).casefold()
    for profile in job_profiles:
        required = list(profile.get("required_skills") or [])
        preferred = list(profile.get("preferred_skills") or [])
        report = score_match(
            candidate.get("skills", []),
            required,
            preferred,
            candidate.get("certificates", []),
            projects=candidate.get("projects", []),
            internships=candidate.get("internships", []),
            awards=candidate.get("awards", []),
            education=str(candidate.get("education") or ""),
            major=str(candidate.get("major") or ""),
            self_summary=str(candidate.get("self_summary") or "")[:4000],
            job_name=str(profile.get("name") or ""),
            job_description=str(profile.get("description") or ""),
            job_domain=str(profile.get("domain") or ""),
            job_level=str(profile.get("level") or ""),
        )
        job_name = str(profile.get("name") or "")
        focus_hits = [term for term in JOB_FOCUS_TERMS if term in job_name.casefold() and term in candidate_text]
        focus_score = min(12.0, len(focus_hits) * 12.0)
        ranked.append(
            {
                "job_name": job_name,
                "job_id": profile.get("id"),
                "total_score": report["total_score"],
                "ranking_score": round(report["total_score"] + focus_score, 1),
                "focus_score": focus_score,
                "focus_hits": focus_hits,
                "required_skill_score": report["required_skill_score"],
                "scenario_score": report["scenario_score"],
                "report": report,
            }
        )
    ranked.sort(key=lambda item: (item["ranking_score"], item["required_skill_score"], item["scenario_score"], str(item["job_name"])), reverse=True)
    return ranked


def canonical_skill(value: str) -> str:
    raw = str(value or "").strip().lower()
    compact = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", raw)
    return _ALIAS_LOOKUP.get(compact, re.sub(r"\s+", " ", raw))


def _skill_row(item: Any) -> tuple[str, str, str]:
    if isinstance(item, dict):
        return str(item.get("name") or "").strip(), str(item.get("level") or "").strip(), str(item.get("evidence") or "").strip()
    return str(item or "").strip(), "", ""


def _experience_sources(projects: list[Any], internships: list[Any], self_summary: str) -> list[dict[str, str]]:
    rows = []
    for label, items in (("项目", projects), ("实习", internships)):
        for index, item in enumerate(items):
            text = _item_text(item)
            if text:
                rows.append({"source": f"{label}{index + 1}", "text": text})
    if self_summary.strip():
        rows.append({"source": "个人总结", "text": self_summary.strip()})
    return rows


def _item_text(item: Any) -> str:
    if isinstance(item, dict):
        return " ".join(str(value) for value in item.values() if value not in (None, "", []))
    return str(item or "").strip()


def _evaluate_skill_group(
    targets: list[str],
    explicit: dict[str, dict[str, str]],
    evidence_text: str,
    weights: dict[str, float] | None,
) -> dict:
    if not targets:
        return {"score": 100.0, "matched": [], "missing": [], "evidence": [], "summary": "岗位未配置该类技能要求"}
    weighted_total = 0.0
    weighted_hit = 0.0
    matched, missing, evidence = [], [], []
    for target in targets:
        canonical = canonical_skill(target)
        weight = max(0.1, float((weights or {}).get(target, 1.0)))
        weighted_total += weight
        if canonical in explicit:
            weighted_hit += weight
            matched.append(target)
            row = explicit[canonical]
            note = f"技能清单：{row['name']}"
            if row.get("level"):
                note += f"（{row['level']}）"
            evidence.append(note)
        elif _contains_skill(evidence_text, canonical):
            weighted_hit += weight * 0.72
            matched.append(target)
            evidence.append(f"经历文本提及：{target}（按间接证据计分）")
        else:
            missing.append(target)
    score = round(weighted_hit / weighted_total * 100, 1) if weighted_total else 100.0
    summary = f"覆盖 {len(matched)}/{len(targets)} 项；直接技能证据优先，经历文本命中按 72% 权重计入"
    return {"score": score, "matched": matched, "missing": missing, "evidence": evidence[:6], "summary": summary}


def _contains_skill(text: str, canonical: str) -> bool:
    lowered = text.lower()
    aliases = SKILL_ALIAS_GROUPS.get(canonical, {canonical}) | {canonical}
    for alias in aliases:
        alias = alias.lower().strip()
        if not alias:
            continue
        if re.fullmatch(r"[a-z0-9 .+/#-]+", alias):
            pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
            if re.search(pattern, lowered):
                return True
        elif alias in lowered:
            return True
    return False


def _project_score(projects: list[Any], internships: list[Any], target_skills: list[str]) -> tuple[float, dict]:
    sources = _experience_sources(projects, internships, "")
    if not sources:
        return 15.0, {"matched": [], "missing": ["缺少项目或实习证据"], "evidence": [], "summary": "未提供可核验的项目或实习经历"}
    text = "\n".join(item["text"] for item in sources)
    relevant = [skill for skill in target_skills if _contains_skill(text, canonical_skill(skill))]
    relevance_ratio = len(relevant) / max(1, len(target_skills))
    quantified = bool(re.search(r"\d+(?:\.\d+)?\s*(?:%|万|千|ms|秒|人|条|次|倍|个)", text, re.I))
    action_count = sum(token in text for token in ("负责", "设计", "实现", "开发", "搭建", "优化", "部署", "上线", "主导", "解决"))
    result_count = sum(token in text for token in ("提升", "降低", "减少", "完成", "落地", "达到", "节省", "结果"))
    score = 32 + min(18, len(sources) * 6) + min(28, relevance_ratio * 55) + min(12, action_count * 2) + min(10, result_count * 2)
    if quantified:
        score += 8
    evidence = [item["text"][:120] for item in sources[:3]]
    missing = []
    if not quantified:
        missing.append("缺少量化结果")
    if action_count == 0:
        missing.append("个人职责不明确")
    if not relevant:
        missing.append("经历与岗位技能关联较弱")
    return round(min(100, score), 1), {
        "matched": relevant[:8],
        "missing": missing,
        "evidence": evidence,
        "summary": f"识别到 {len(sources)} 段经历、{len(relevant)} 项岗位技能证据" + ("，包含量化结果" if quantified else ""),
    }


def _tool_score(target_skills: list[str], explicit: dict[str, dict[str, str]], evidence_text: str) -> tuple[float, dict]:
    target_tools = [skill for skill in target_skills if canonical_skill(skill) in TOOL_SKILLS]
    if not target_tools:
        return 60.0, {"matched": [], "missing": [], "evidence": [], "summary": "岗位画像未单独配置工具要求，采用中性分"}
    matched = [skill for skill in target_tools if canonical_skill(skill) in explicit or _contains_skill(evidence_text, canonical_skill(skill))]
    score = round(len(matched) / len(target_tools) * 100, 1)
    return score, {
        "matched": matched,
        "missing": [skill for skill in target_tools if skill not in matched],
        "evidence": [f"已提供 {skill} 使用证据" for skill in matched[:6]],
        "summary": f"覆盖岗位工具要求 {len(matched)}/{len(target_tools)} 项",
    }


def _scenario_score(
    projects: list[Any],
    internships: list[Any],
    self_summary: str,
    target_skills: list[str],
    job_name: str,
    job_description: str,
    job_domain: str,
) -> tuple[float, dict]:
    sources = _experience_sources(projects, internships, self_summary)
    if not sources:
        return 15.0, {"matched": [], "missing": ["缺少业务场景描述"], "evidence": [], "summary": "没有可用于判断岗位场景迁移能力的经历"}
    text = "\n".join(item["text"] for item in sources)
    relevant = [skill for skill in target_skills if _contains_skill(text, canonical_skill(skill))]
    domain_tokens = [token for token in (job_domain, job_name.replace("工程师", "").replace("专员", "")) if token and len(token) >= 2]
    domain_hits = [token for token in domain_tokens if token.lower() in text.lower()]
    responsibility_hits = sum(token in text for token in ("需求", "方案", "业务", "用户", "数据", "服务", "系统", "指标", "交付", "协作"))
    score = 28 + min(42, len(relevant) / max(1, min(8, len(target_skills))) * 50) + min(18, responsibility_hits * 3) + min(12, len(domain_hits) * 6)
    evidence = [item["text"][:120] for item in sources[:3]]
    missing = [] if relevant else ["未识别到与目标岗位直接相关的场景证据"]
    if job_description and not any(token in text for token in ("需求", "方案", "业务", "系统", "数据", "用户")):
        missing.append("缺少职责或业务结果描述")
    return round(min(100, score), 1), {
        "matched": _unique(domain_hits + relevant[:6]),
        "missing": missing,
        "evidence": evidence,
        "summary": f"从项目、实习和个人总结中识别到 {len(relevant)} 项岗位关联信号",
    }


def _certificate_score(
    certificates: list[Any],
    awards: list[Any],
    job_description: str,
    target_skills: list[str],
    recommended_certificates: list[str],
) -> tuple[float, dict]:
    rows = [_item_text(item) for item in certificates + awards if _item_text(item)]
    if recommended_certificates:
        matched = [target for target in recommended_certificates if any(_certificate_matches(row, target) for row in rows)]
        missing = [target for target in recommended_certificates if target not in matched]
        if not rows:
            return 35.0, {
                "matched": [],
                "missing": missing,
                "evidence": [],
                "summary": "岗位关联证书均为建议项，不是强制任职条件；当前未提供证书证据",
            }
        score = 55 + (40 * len(matched) / len(recommended_certificates)) + min(5, max(0, len(rows) - len(matched)) * 2)
        return round(min(100, score), 1), {
            "matched": matched,
            "missing": missing,
            "evidence": rows[:6],
            "summary": f"岗位目录建议 {len(recommended_certificates)} 项证书，已匹配 {len(matched)} 项；证书维度仅占 5%",
        }
    if not rows:
        return 25.0, {"matched": [], "missing": ["未提供证书或成果"], "evidence": [], "summary": "证书成果权重仅占 5%，不会替代项目能力证据"}
    context = f"{job_description} {' '.join(target_skills)}".lower()
    relevant = [item for item in rows if any(token in context for token in _certificate_tokens(item))]
    score = min(100, 55 + len(rows) * 8 + len(relevant) * 12)
    return float(score), {
        "matched": relevant or rows[:4],
        "missing": [] if relevant else ["成果与目标岗位的直接关联需要补充说明"],
        "evidence": rows[:6],
        "summary": f"提供 {len(certificates)} 项证书、{len(awards)} 项竞赛或成果",
    }


def _certificate_matches(candidate: str, target: str) -> bool:
    candidate_norm = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", candidate.casefold())
    target_norm = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", target.casefold())
    aliases = {
        "计算机技术与软件专业技术资格": ("软考", "计算机技术与软件专业技术资格", "软件水平考试"),
        "通信专业技术人员职业资格": ("通信专业技术人员职业资格", "通信工程师", "通信专业技术"),
        "统计专业技术资格": ("统计专业技术资格", "统计师", "统计专业资格"),
    }
    return target_norm in candidate_norm or any(
        re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", alias.casefold()) in candidate_norm
        for alias in aliases.get(target, (target,))
    )


def _certificate_tokens(value: str) -> list[str]:
    lowered = value.lower()
    known = ("python", "java", "网络", "安全", "项目", "数据", "ai", "人工智能", "云", "软考", "pmp", "cpa", "英语")
    return [token for token in known if token in lowered]


def _confidence_score(*flags: bool) -> float:
    weights = (25, 20, 10, 10, 25, 10)
    return float(sum(weight for weight, flag in zip(weights, flags) if flag))


def _dimension(name: str, score: float, weight: int, detail: dict) -> dict:
    return {
        "name": name,
        "score": round(float(score), 1),
        "weight": weight,
        "summary": detail.get("summary", ""),
        "matched": detail.get("matched", []),
        "missing": detail.get("missing", []),
        "evidence": detail.get("evidence", []),
    }


def _build_suggestions(
    missing_required: list[str],
    missing_preferred: list[str],
    project_score: float,
    scenario_score: float,
    certificates: list[Any],
) -> list[str]:
    rows = [f"优先补齐必备技能 {skill}：完成一个可运行的小项目，并在简历中写明个人职责与结果" for skill in missing_required[:3]]
    if project_score < 65:
        rows.append("重写项目经历，至少写清背景、个人行动、使用技术和可量化结果")
    if scenario_score < 65:
        rows.append("补充一次与目标岗位接近的真实业务场景，说明需求、约束、方案和验证方式")
    if missing_preferred:
        rows.append(f"在必备能力稳定后补充加分技能：{'、'.join(missing_preferred[:3])}")
    if not certificates:
        rows.append("证书不是决定项；如已有课程、竞赛或开源成果，可作为辅助证据补充")
    return _unique(rows)[:6] or ["当前核心能力覆盖较好，下一步应补充更具体的项目结果与岗位场景证据"]


def _unique(items: list[Any]) -> list[Any]:
    result = []
    seen = set()
    for item in items:
        marker = str(item)
        if marker not in seen:
            result.append(item)
            seen.add(marker)
    return result
