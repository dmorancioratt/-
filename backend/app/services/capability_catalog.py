"""Unified occupation-capability catalog shared by graph, matching and learning flows.

The public sources describe different layers: MOHRSS publishes Chinese occupations and
qualification schedules, O*NET supplies occupation/skill observations, ESCO supplies a
cross-border classification, and WEF supplies trend signals.  This module keeps those
layers distinct and records when SkillBridge performs a local mapping.
"""

from __future__ import annotations

import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    CertificateEntity,
    DataSource,
    ExternalCatalogItem,
    JobCertificateRelation,
    JobEntity,
    JobSkillRelation,
    SkillEntity,
)


CATALOG_VERSION = "2026.08-authority-v2"

OFFICIAL_NEW_JOBS: dict[str, dict] = {
    "数字孪生工程技术人员": {
        "domain": "产业数字化",
        "job_type": "工程技术",
        "description": "从事数字孪生系统建模、集成、仿真与应用的工程技术人员。",
        "onet": ("15-1299.08", "Computer Systems Engineers/Architects"),
        "skills": ["数字孪生", "三维建模", "仿真分析", "物联网协议", "数据治理", "Python", "数据可视化", "边缘计算", "云计算架构", "项目管理", "安全合规", "系统集成"],
    },
    "具身智能机器人应用技术员": {
        "domain": "智能系统",
        "job_type": "应用技术",
        "description": "面向具身智能机器人部署、调试、应用与运维的新职业。",
        "onet": ("17-3024.01", "Robotics Technicians"),
        "skills": ["具身智能", "机器人", "计算机视觉", "Python", "深度学习", "PyTorch", "模型部署", "传感器数据处理", "边缘计算", "现场调试", "Linux", "安全合规"],
    },
    "运动数据分析师": {
        "domain": "数据技术",
        "job_type": "数据分析",
        "description": "运用数据分析方法处理运动、训练和表现数据的新职业。",
        "onet": ("15-2051.00", "Data Scientists"),
        "skills": ["统计分析", "Python", "Pandas", "数据可视化", "时序数据", "数据质量", "机器学习", "BI 分析", "用户画像", "A/B 测试", "需求分析", "项目管理"],
    },
    "智能体开发员": {
        "domain": "人工智能",
        "job_type": "应用研发",
        "description": "面向智能体应用设计、开发、编排、评测与维护的新工种。",
        "onet": ("15-1252.00", "Software Developers"),
        "skills": ["Python", "智能体编排", "大模型", "RAG", "Prompt Engineering", "LangChain", "工作流引擎", "OpenAPI", "模型评估", "Docker", "安全合规", "数据质量"],
    },
}

WEF_TREND_JOBS: dict[str, dict] = {
    "大数据专家": {
        "domain": "数据技术", "job_type": "全球趋势岗位", "description": "WEF 2025 报告列出的快速增长岗位方向。",
        "onet": ("15-2051.00", "Data Scientists"),
        "skills": ["AI 与大数据", "Python", "SQL", "Spark", "数据治理", "数据仓库", "统计分析", "机器学习", "数据可视化", "云计算架构", "数据质量", "分析性思维"],
    },
    "金融科技工程师": {
        "domain": "软件研发", "job_type": "全球趋势岗位", "description": "WEF 2025 报告列出的快速增长岗位方向。",
        "onet": ("15-1252.00", "Software Developers"),
        "skills": ["Python", "Java", "SQL", "微服务", "RESTful API", "数据质量", "安全合规", "风险策略", "云计算架构", "Docker", "项目管理", "技术素养"],
    },
    "AI 与机器学习专家": {
        "domain": "人工智能", "job_type": "全球趋势岗位", "description": "WEF 2025 报告列出的快速增长岗位方向。",
        "onet": ("15-2051.00", "Data Scientists"),
        "skills": ["AI 与大数据", "Python", "机器学习", "深度学习", "PyTorch", "TensorFlow", "特征工程", "模型评估", "模型部署", "数据质量", "分析性思维", "技术素养"],
    },
    "软件与应用开发人员": {
        "domain": "软件研发", "job_type": "全球趋势岗位", "description": "WEF 2025 报告列出的快速增长岗位方向。",
        "onet": ("15-1252.00", "Software Developers"),
        "skills": ["Java", "Python", "TypeScript", "RESTful API", "微服务", "Git", "Docker", "CI/CD", "SQL", "测试自动化", "技术素养", "项目管理"],
    },
    "信息安全分析师": {
        "domain": "安全合规", "job_type": "全球趋势岗位", "description": "WEF 2025 报告列出的快速增长岗位方向。",
        "onet": ("15-1212.00", "Information Security Analysts"),
        "skills": ["网络与网络安全", "Linux", "网络协议", "日志分析", "漏洞扫描", "权限管理", "安全合规", "Python", "风险策略", "云安全", "分析性思维", "技术素养"],
    },
}

CATALOG_JOB_PROFILES = {**OFFICIAL_NEW_JOBS, **WEF_TREND_JOBS}

# O*NET occupations that directly support the competition scope.  We keep the
# official SOC code and English title as provenance, while exposing a concise
# Chinese localization to product users.  The list deliberately excludes rows
# that only happened to mention "data" or "computer" in a broad description.
ONET_LOCALIZED_OCCUPATIONS: dict[str, tuple[str, str, str]] = {
    "11-3021.00": ("信息系统经理", "产业数字化", "技术管理"),
    "11-9121.01": ("临床研究数据协调员", "医疗信息化", "数据管理"),
    "13-1081.01": ("智慧物流工程师", "产业数字化", "工程技术"),
    "13-1161.00": ("市场数据分析师", "数据技术", "数据分析"),
    "13-1161.01": ("搜索营销策略师", "数字内容", "增长技术"),
    "13-2041.00": ("信用数据分析师", "金融科技", "数据分析"),
    "13-2051.00": ("金融量化分析师", "金融科技", "数据分析"),
    "15-1211.00": ("计算机系统分析师", "软件研发", "系统分析"),
    "15-1211.01": ("医疗信息化专家", "医疗信息化", "系统分析"),
    "15-1212.00": ("信息安全分析师", "安全合规", "安全技术"),
    "15-1221.00": ("计算机与信息研究科学家", "人工智能", "科研技术"),
    "15-1231.00": ("计算机网络支持专家", "基础设施", "运维支持"),
    "15-1232.00": ("计算机用户支持专家", "基础设施", "技术支持"),
    "15-1241.00": ("计算机网络架构师", "基础设施", "架构设计"),
    "15-1241.01": ("通信系统工程师", "物联网", "通信技术"),
    "15-1242.00": ("数据库运维工程师", "数据技术", "数据运维"),
    "15-1243.00": ("数据库架构师", "数据技术", "架构设计"),
    "15-1243.01": ("数据仓库专家", "数据技术", "数据工程"),
    "15-1244.00": ("网络与系统管理员", "基础设施", "系统运维"),
    "15-1251.00": ("计算机程序设计师", "软件研发", "软件开发"),
    "15-1252.00": ("软件开发工程师", "软件研发", "软件开发"),
    "15-1253.00": ("软件质量保障工程师", "软件研发", "测试质量"),
    "15-1254.00": ("Web 应用开发工程师", "软件研发", "软件开发"),
    "15-1255.00": ("数字交互界面设计师", "数字内容", "交互设计"),
    "15-1299.01": ("Web 平台运维工程师", "软件研发", "平台运维"),
    "15-1299.02": ("GIS 地理信息技术员", "地理空间", "空间数据"),
    "15-1299.04": ("渗透测试工程师", "安全合规", "安全技术"),
    "15-1299.05": ("信息安全工程师", "安全合规", "安全技术"),
    "15-1299.06": ("数字取证分析师", "安全合规", "安全分析"),
    "15-1299.07": ("区块链工程师", "软件研发", "新兴技术"),
    "15-1299.08": ("计算机系统架构师", "软件研发", "架构设计"),
    "15-2011.00": ("精算数据分析师", "金融科技", "数据分析"),
    "15-2031.00": ("运筹优化分析师", "数据技术", "算法分析"),
    "15-2041.00": ("统计分析师", "数据技术", "数据分析"),
    "15-2041.01": ("生物统计师", "医疗信息化", "数据分析"),
    "15-2051.00": ("数据科学家", "数据技术", "数据科学"),
    "15-2051.01": ("商业智能分析师", "数据技术", "商业分析"),
    "15-2051.02": ("临床数据经理", "医疗信息化", "数据管理"),
    "15-2099.01": ("生物信息技术员", "医疗信息化", "科研技术"),
    "17-1021.00": ("数字地图工程师", "地理空间", "空间数据"),
    "17-2031.00": ("生物医学智能工程师", "医疗信息化", "智能系统"),
    "17-2061.00": ("计算机硬件工程师", "智能系统", "硬件研发"),
    "17-2072.00": ("电子系统工程师", "智能系统", "硬件研发"),
    "17-2112.01": ("人因与智能交互工程师", "智能系统", "交互设计"),
    "17-2141.02": ("智能汽车系统工程师", "智能系统", "智能制造"),
    "17-2199.08": ("机器人工程师", "智能系统", "机器人技术"),
    "17-3024.00": ("机电一体化技术员", "智能制造", "应用技术"),
    "17-3024.01": ("机器人应用技术员", "智能制造", "应用技术"),
    "19-1029.01": ("生物信息科学家", "医疗信息化", "科研技术"),
    "19-2021.00": ("气象数据科学家", "地理空间", "数据科学"),
    "19-2041.00": ("环境数据分析师", "地理空间", "数据分析"),
    "19-2099.01": ("遥感科学家", "地理空间", "空间数据"),
    "19-3011.00": ("经济数据分析师", "数据技术", "数据分析"),
    "19-3022.00": ("调查数据研究员", "数据技术", "数据研究"),
    "19-3099.01": ("智慧交通规划师", "产业数字化", "规划分析"),
    "19-4012.01": ("智慧农业技术员", "智慧农业", "应用技术"),
    "19-4061.00": ("社会数据研究助理", "数据技术", "数据研究"),
    "25-1021.00": ("计算机科学讲师", "教育科技", "技术教育"),
    "25-4022.00": ("数字知识资源管理员", "教育科技", "知识管理"),
    "27-1014.00": ("数字特效与动画设计师", "数字内容", "内容技术"),
    "29-9021.00": ("健康信息技术专家", "医疗信息化", "系统分析"),
    "33-3021.06": ("多源情报分析师", "安全合规", "数据分析"),
    "43-9111.00": ("统计数据助理", "数据技术", "数据处理"),
    "49-2021.00": ("无线通信设备工程师", "物联网", "通信技术"),
    "51-9161.00": ("数控设备操作技术员", "智能制造", "应用技术"),
    "51-9162.00": ("数控系统编程工程师", "智能制造", "软件开发"),
}

ESSENTIAL_SKILL_ZH = {
    "Active Listening": "主动倾听", "Reading Comprehension": "阅读理解", "Speaking": "口头表达",
    "Critical Thinking": "批判性思维", "Monitoring": "过程监控", "Writing": "书面表达",
    "Active Learning": "主动学习", "Mathematics": "数学能力", "Learning Strategies": "学习策略", "Science": "科学素养",
}

DOMAIN_CORE_SKILLS: dict[str, list[str]] = {
    "人工智能": ["Python", "机器学习", "模型评估", "数据质量"],
    "数据技术": ["SQL", "数据治理", "统计分析", "数据质量"],
    "软件研发": ["软件工程", "Git", "测试自动化", "系统设计"],
    "安全合规": ["网络安全", "风险策略", "日志分析", "安全合规"],
    "基础设施": ["Linux", "网络协议", "系统运维", "安全合规"],
    "物联网": ["物联网协议", "传感器数据处理", "边缘计算", "网络协议"],
    "智能系统": ["系统集成", "传感器数据处理", "边缘计算", "模型部署"],
    "智能制造": ["智能制造", "现场调试", "系统集成", "项目管理"],
    "产业数字化": ["需求分析", "业务流程建模", "数据治理", "项目管理"],
    "金融科技": ["Python", "SQL", "统计分析", "风险策略"],
    "医疗信息化": ["数据治理", "统计分析", "隐私保护", "系统集成"],
    "地理空间": ["GIS", "数据可视化", "空间分析", "Python"],
    "智慧农业": ["物联网协议", "GIS", "数据分析", "现场调试"],
    "教育科技": ["知识管理", "数字资源管理", "数据分析", "用户研究"],
    "数字内容": ["UI/UX 设计", "数据可视化", "用户研究", "内容审核"],
}

ONET_LOCALIZED_BY_NAME = {
    name: (code, f"O*NET occupation {code}")
    for code, (name, _domain, _job_type) in ONET_LOCALIZED_OCCUPATIONS.items()
}


def _contains_any(value: str, tokens: tuple[str, ...]) -> bool:
    lowered = value.casefold()
    return any(token.casefold() in lowered for token in tokens)


ONET_RULES: list[tuple[tuple[str, ...], tuple[str, str]]] = [
    (("数据仓库",), ("15-1243.01", "Data Warehousing Specialists")),
    (("数据库管理员", "DBA"), ("15-1242.00", "Database Administrators")),
    (("网络安全",), ("15-1212.00", "Information Security Analysts")),
    (("渗透测试",), ("15-1299.04", "Penetration Testers")),
    (("云安全", "内容风控"), ("15-1299.05", "Information Security Engineers")),
    (("网络工程",), ("15-1241.00", "Computer Network Architects")),
    (("测试开发",), ("15-1253.00", "Software Quality Assurance Analysts and Testers")),
    (("前端",), ("15-1254.00", "Web Developers")),
    (("UI/UX",), ("15-1255.00", "Web and Digital Interface Designers")),
    (("数据分析", "BI 可视化", "机器学习", "算法"), ("15-2051.00", "Data Scientists")),
    (("数据治理", "数据产品", "数据资产"), ("15-1243.00", "Database Architects")),
    (("大模型", "智能体", "Java", "开发工程师", "DevOps", "SRE", "低代码"), ("15-1252.00", "Software Developers")),
    (("物联网", "智能系统", "技术支持"), ("15-1299.08", "Computer Systems Engineers/Architects")),
    (("项目经理",), ("11-3021.00", "Computer and Information Systems Managers")),
    (("产品经理", "解决方案", "实施顾问", "售前"), ("15-1211.00", "Computer Systems Analysts")),
]


SKILL_CATEGORY = {
    "数字孪生": "产业数字化", "三维建模": "工程建模", "仿真分析": "工程建模", "系统集成": "工程交付",
    "具身智能": "人工智能", "机器人": "智能系统", "现场调试": "工程交付", "时序数据": "数据技术",
    "AI 与大数据": "趋势能力", "网络与网络安全": "趋势能力", "技术素养": "通用能力",
    "创造性思维": "通用能力", "韧性、灵活性与敏捷性": "通用能力", "好奇心与终身学习": "通用能力", "分析性思维": "通用能力",
}


def resolve_onet(job: JobEntity | str) -> tuple[str, str]:
    name = job if isinstance(job, str) else job.name
    if name in CATALOG_JOB_PROFILES:
        return CATALOG_JOB_PROFILES[name]["onet"]
    if name in ONET_LOCALIZED_BY_NAME:
        return ONET_LOCALIZED_BY_NAME[name]
    for tokens, profile in ONET_RULES:
        if _contains_any(name, tokens):
            return profile
    return "15-1299.00", "Computer Occupations, All Other"


def _source_map(db: Session) -> dict[str, DataSource]:
    return {row.source_key: row for row in db.scalars(select(DataSource)).all() if row.source_key}


def _source_ref(source: DataSource | None) -> dict:
    if not source:
        return {}
    return {
        "source_key": source.source_key,
        "source_name": source.source_name,
        "publisher": source.publisher,
        "version": source.version,
        "published_at": source.published_at.isoformat() if source.published_at else None,
        "source_url": source.source_url,
    }


def _materialize_onet_occupations(
    db: Session,
    skill_by_name: dict[str, SkillEntity],
    onet_source: DataSource | None,
) -> int:
    """Promote the curated digital subset of O*NET into the shared graph."""
    occupation_rows = {
        row.external_id: row
        for row in db.scalars(
            select(ExternalCatalogItem).where(
                ExternalCatalogItem.source_key == "onet_30_3",
                ExternalCatalogItem.item_type == "occupation",
                ExternalCatalogItem.external_id.in_(list(ONET_LOCALIZED_OCCUPATIONS)),
            )
        ).all()
    }
    created = 0
    source_url = onet_source.source_url if onet_source else "https://www.onetcenter.org/database.html"
    for code, (name, domain, job_type) in ONET_LOCALIZED_OCCUPATIONS.items():
        external = occupation_rows.get(code)
        external_title = external.name if external else f"O*NET occupation {code}"
        job = db.scalar(select(JobEntity).where(JobEntity.name == name))
        if job is not None:
            continue

        job = JobEntity(
            name=name,
            domain=domain,
            job_type=job_type,
            level="中级",
            description=f"{name}负责{domain}领域的分析、设计、实施、验证与持续改进，岗位边界依据 O*NET 30.3 职业定义进行中文本地化。",
            is_emerging=False,
            status="active",
            version=CATALOG_VERSION,
            evidence=(
                f"权威职业映射：O*NET 30.3 {code} {external_title}（{source_url}）；"
                "中文岗位名、领域和能力组合由 SkillBridge 本地化，保留原始 SOC 编码以便核验。"
            ),
        )
        db.add(job)
        db.flush()

        candidates: list[tuple[str, str, str]] = []
        for skill_name in DOMAIN_CORE_SKILLS.get(domain, ["需求分析", "项目管理", "数据质量", "系统集成"]):
            candidates.append((skill_name, "requires", f"{domain}领域核心能力"))

        essential_rows = db.scalars(
            select(ExternalCatalogItem).where(
                ExternalCatalogItem.source_key == "onet_30_3",
                ExternalCatalogItem.item_type == "essential_skill",
                ExternalCatalogItem.external_id.like(f"{code}:%"),
            )
        ).all()
        essential_rows = sorted(
            essential_rows,
            key=lambda row: float(json.loads(row.payload_json or "{}").get("importance") or 0),
            reverse=True,
        )[:4]
        for row in essential_rows:
            candidates.append((ESSENTIAL_SKILL_ZH.get(row.name, row.name), "requires", f"O*NET 核心技能：{row.name}"))

        software_rows = db.scalars(
            select(ExternalCatalogItem).where(
                ExternalCatalogItem.source_key == "onet_30_3",
                ExternalCatalogItem.item_type == "software_skill",
                ExternalCatalogItem.external_id.like(f"{code}:%"),
            )
        ).all()
        software_rows = sorted(
            software_rows,
            key=lambda row: (
                not bool(json.loads(row.payload_json or "{}").get("hot_technology")),
                not bool(json.loads(row.payload_json or "{}").get("in_demand")),
                row.name.casefold(),
            ),
        )[:6]
        for row in software_rows:
            candidates.append((row.name[:120], "prefers", "O*NET 热门或紧缺软件技能"))

        seen: set[str] = set()
        for index, (skill_name, relation_type, evidence_label) in enumerate(candidates):
            if not skill_name or skill_name in seen:
                continue
            seen.add(skill_name)
            skill = skill_by_name.get(skill_name)
            if skill is None:
                skill = SkillEntity(
                    name=skill_name,
                    category="工具平台" if relation_type == "prefers" else SKILL_CATEGORY.get(skill_name, "通用能力"),
                    description=f"{skill_name} 是 {name} 岗位画像中的可验证能力或工具。",
                    evidence=f"来源或映射依据：O*NET 30.3 {code} {external_title}（{source_url}）。",
                )
                db.add(skill)
                db.flush()
                skill_by_name[skill_name] = skill
            db.add(
                JobSkillRelation(
                    job_id=job.id,
                    skill_id=skill.id,
                    relation_type=relation_type,
                    weight=round(max(0.55, 1.0 - index * 0.035), 2),
                    evidence=f"{name} → {skill_name}：{evidence_label}，对应 O*NET 30.3 {code}。",
                )
            )
        created += 1
    db.flush()
    return created


def sync_capability_catalog(db: Session) -> dict:
    """Materialize official occupations, shared skills and job-certificate links."""
    sources = _source_map(db)
    mohrss = sources.get("mohrss_new_occupations_2026")
    onet = sources.get("onet_30_3")
    esco = sources.get("esco_1_2_1")
    wef = sources.get("wef_future_jobs_2025")
    qualifications = sources.get("mohrss_qualification_2026")

    skill_by_name = {row.name: row for row in db.scalars(select(SkillEntity)).all()}
    for name, profile in CATALOG_JOB_PROFILES.items():
        job = db.scalar(select(JobEntity).where(JobEntity.name == name))
        if not job:
            job = JobEntity(name=name)
            db.add(job)
        job.domain = profile["domain"]
        job.job_type = profile["job_type"]
        job.level = "中级"
        job.description = profile["description"]
        job.is_emerging = True
        job.status = "proposed" if name in OFFICIAL_NEW_JOBS else "trend"
        job.version = CATALOG_VERSION
        code, title = profile["onet"]
        if name in OFFICIAL_NEW_JOBS:
            job.evidence = (
                f"职业名称与状态：人社部 2026 年新职业公示（{mohrss.source_url if mohrss else ''}）；"
                f"能力映射参照 O*NET 30.3 {code} {title} 与 ESCO 1.2.1，属于 SkillBridge 本地映射，不代表公示已正式发布国家职业标准。"
            )
        else:
            job.evidence = (
                f"趋势岗位：WEF Future of Jobs 2025（{wef.source_url if wef else ''}）；"
                f"能力映射参照 O*NET 30.3 {code} {title}，中文岗位名与能力组合属于 SkillBridge 本地化结果。"
            )
        db.flush()
        db.execute(delete(JobSkillRelation).where(JobSkillRelation.job_id == job.id))
        for index, skill_name in enumerate(profile["skills"]):
            skill = skill_by_name.get(skill_name)
            if not skill:
                skill = SkillEntity(
                    name=skill_name,
                    category=SKILL_CATEGORY.get(skill_name, "专业能力"),
                    description=f"{skill_name} 用于描述数字技术岗位的可验证能力。",
                    evidence="",
                )
                db.add(skill)
                db.flush()
                skill_by_name[skill_name] = skill
            db.add(JobSkillRelation(
                job_id=job.id,
                skill_id=skill.id,
                relation_type="requires" if index < 8 else "prefers",
                weight=round(1.0 - index * 0.035, 2),
                evidence=f"{name} → {skill_name}：基于人社部职业描述并参照 O*NET 30.3 {code} {title} 进行本地能力映射。",
            ))

    localized_onet_jobs = _materialize_onet_occupations(db, skill_by_name, onet)

    trend_items = db.scalars(select(ExternalCatalogItem).where(
        ExternalCatalogItem.source_key == "wef_future_jobs_2025",
        ExternalCatalogItem.item_type == "skill",
    )).all()
    for item in trend_items:
        skill = skill_by_name.get(item.name)
        if not skill:
            skill = SkillEntity(name=item.name, category=SKILL_CATEGORY.get(item.name, item.category), description=item.description, evidence="")
            db.add(skill)
            db.flush()
            skill_by_name[item.name] = skill

    exact_onet = {
        row.name.casefold(): row
        for row in db.scalars(select(ExternalCatalogItem).where(
            ExternalCatalogItem.source_key == "onet_30_3",
            ExternalCatalogItem.item_type.in_(["software_skill", "essential_skill"]),
        )).all()
    }
    wef_by_name = {item.name: item for item in trend_items}
    for skill in skill_by_name.values():
        external = exact_onet.get(skill.name.casefold())
        trend = wef_by_name.get(skill.name)
        if external:
            payload = json.loads(external.payload_json or "{}")
            skill.evidence = (
                f"O*NET 30.3 可核验技能条目（职业 {payload.get('onet_soc_code', '')}，{onet.source_url if onet else ''}）；"
                "中文分类由 SkillBridge 本地统一。"
            )
        elif trend:
            skill.evidence = f"WEF Future of Jobs 2025 趋势技能（{wef.source_url if wef else ''}）；岗位关联由 SkillBridge 本地映射。"
        else:
            skill.evidence = (
                f"能力概念参照 O*NET 30.3（{onet.source_url if onet else ''}）与 ESCO 1.2.1（{esco.source_url if esco else ''}）；"
                "名称、分类和岗位关联为 SkillBridge 本地化结果。"
            )

    for job in db.scalars(select(JobEntity)).all():
        if job.name not in CATALOG_JOB_PROFILES:
            code, title = resolve_onet(job)
            job.version = CATALOG_VERSION
            job.evidence = (
                f"岗位能力画像参照 O*NET 30.3 {code} {title}（{onet.source_url if onet else ''}）和 ESCO 1.2.1（{esco.source_url if esco else ''}）；"
                "中文岗位名称与能力组合为 SkillBridge 本地映射，需结合真实 JD 持续校准。"
            )
        code, title = resolve_onet(job)
        for relation in job.skill_relations:
            relation.evidence = f"{job.name} → {relation.skill.name}：参照 O*NET 30.3 {code} {title}，由 SkillBridge 映射为{('必备' if relation.relation_type == 'requires' else '加分')}能力。"

    certificate_items = db.scalars(select(ExternalCatalogItem).where(ExternalCatalogItem.item_type == "certificate")).all()
    cert_by_name: dict[str, CertificateEntity] = {}
    for item in certificate_items:
        payload = json.loads(item.payload_json or "{}")
        cert = db.scalar(select(CertificateEntity).where(CertificateEntity.name == item.name))
        if not cert:
            cert = CertificateEntity(name=item.name)
            db.add(cert)
        cert.category = item.category
        cert.issuer = qualifications.publisher if qualifications else "中华人民共和国人力资源和社会保障部"
        cert.levels = json.dumps(payload.get("levels", []), ensure_ascii=False)
        cert.description = item.description
        cert.source_key = item.source_key
        cert.external_id = item.external_id
        cert.evidence = f"列入 2026 年度专业技术人员职业资格考试工作计划：{qualifications.source_url if qualifications else ''}"
        cert_by_name[item.name] = cert
    db.flush()

    db.execute(delete(JobCertificateRelation))
    for job in db.scalars(select(JobEntity)).all():
        recommended = _recommended_certificates(job)
        for name, weight, reason in recommended:
            cert = cert_by_name.get(name)
            if not cert:
                continue
            db.add(JobCertificateRelation(
                job_id=job.id,
                certificate_id=cert.id,
                relation_type="recommended",
                weight=weight,
                evidence=(
                    f"{name} 已列入人社部 2026 年考试计划；因“{reason}”与 {job.name} 的能力领域相关，"
                    "系统标记为建议项而非强制任职条件。"
                ),
            ))
    db.flush()
    return {
        "catalog_version": CATALOG_VERSION,
        "jobs": len(db.scalars(select(JobEntity)).all()),
        "skills": len(db.scalars(select(SkillEntity)).all()),
        "certificates": len(cert_by_name),
        "skill_relations": len(db.scalars(select(JobSkillRelation)).all()),
        "certificate_relations": len(db.scalars(select(JobCertificateRelation)).all()),
        "localized_onet_jobs": localized_onet_jobs,
    }


def _recommended_certificates(job: JobEntity) -> list[tuple[str, float, str]]:
    value = f"{job.name} {job.domain} {job.job_type}"
    rows: list[tuple[str, float, str]] = []
    if _contains_any(value, ("软件", "开发", "人工智能", "数据", "云", "安全", "系统", "项目经理", "产品经理", "数字孪生", "机器人", "UI/UX")):
        rows.append(("计算机技术与软件专业技术资格", 0.72, "计算机与软件工程能力"))
    if _contains_any(value, ("通信", "网络", "物联网", "云计算", "技术支持", "SRE")):
        rows.append(("通信专业技术人员职业资格", 0.68, "通信网络与基础设施能力"))
    if _contains_any(value, ("数据分析", "统计", "BI", "运动数据")):
        rows.append(("统计专业技术资格", 0.75, "统计分析与数据解释能力"))
    return rows or [("计算机技术与软件专业技术资格", 0.55, "通用数字技术能力")]


def job_authority(db: Session, job: JobEntity) -> dict:
    sources = _source_map(db)
    code, title = resolve_onet(job)
    refs = [_source_ref(sources.get("onet_30_3")), _source_ref(sources.get("esco_1_2_1"))]
    if job.name in OFFICIAL_NEW_JOBS:
        refs.insert(0, _source_ref(sources.get("mohrss_new_occupations_2026")))
    elif job.name in WEF_TREND_JOBS:
        refs.insert(0, _source_ref(sources.get("wef_future_jobs_2025")))
    return {
        "catalog_version": CATALOG_VERSION,
        "mapping_type": "official_occupation_with_local_skill_mapping" if job.name in OFFICIAL_NEW_JOBS else "trend_job_with_local_skill_mapping" if job.name in WEF_TREND_JOBS else "local_job_profile_mapped_to_authoritative_taxonomy",
        "onet_soc_code": code,
        "onet_title": title,
        "sources": [ref for ref in refs if ref],
    }


def job_requirements(db: Session, job: JobEntity) -> dict:
    skills = sorted(job.skill_relations, key=lambda row: row.weight, reverse=True)
    certificates = sorted(job.certificate_relations, key=lambda row: row.weight, reverse=True)
    return {
        "required_skills": [row.skill.name for row in skills if row.relation_type == "requires"],
        "preferred_skills": [row.skill.name for row in skills if row.relation_type != "requires"],
        "skill_details": [
            {
                "id": row.skill.id,
                "name": row.skill.name,
                "category": row.skill.category,
                "relation_type": row.relation_type,
                "weight": row.weight,
                "evidence": row.evidence,
            }
            for row in skills
        ],
        "recommended_certificates": [
            {
                "id": row.certificate.id,
                "name": row.certificate.name,
                "category": row.certificate.category,
                "issuer": row.certificate.issuer,
                "levels": json.loads(row.certificate.levels or "[]"),
                "relation_type": row.relation_type,
                "weight": row.weight,
                "source_key": row.certificate.source_key,
                "evidence": row.evidence,
                "source_evidence": row.certificate.evidence,
            }
            for row in certificates
        ],
    }


def enriched_job(db: Session, job: JobEntity) -> dict:
    payload = {column.name: getattr(job, column.name) for column in job.__table__.columns}
    payload["requirements"] = job_requirements(db, job)
    payload["authority"] = job_authority(db, job)
    return payload
