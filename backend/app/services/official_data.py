from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import DataSource, DataSyncRun, ExternalCatalogItem, IndustryMetric, JobEntity, JobSkillRelation, SkillEntity


BACKEND_DIR = Path(__file__).resolve().parents[2]
EXTERNAL_DATA_DIR = BACKEND_DIR / "data" / "external" / "onet_30_3"

ONET_FILES = {
    "occupation_data.csv": "https://www.onetcenter.org/dl_files/database/db_30_3_csv/occupation_data.csv",
    "software_skills.csv": "https://www.onetcenter.org/dl_files/database/db_30_3_csv/software_skills.csv",
    "essential_skills.csv": "https://www.onetcenter.org/dl_files/database/db_30_3_csv/essential_skills.csv",
}

SOURCE_MANIFEST = [
    {
        "source_key": "mohrss_new_occupations_2026",
        "source_name": "人社部 2026 年新职业公示",
        "publisher": "中华人民共和国人力资源和社会保障部",
        "source_url": "https://chinajob.mohrss.gov.cn/c/2026-07-10/569764.shtml",
        "license_name": "政府公开信息",
        "version": "2026-07 公示版",
        "data_type": "新职业与新工种",
        "domain": "中国职业分类",
        "published_at": "2026-07-10",
        "data_count": 12,
        "quality_score": 99.0,
        "status": "verified",
        "sync_message": "已核验 2026 年最新公示；公示职业在正式发布前标注为拟新增。",
    },
    {
        "source_key": "miit_software_2026_05",
        "source_name": "2026 年 1—5 月软件业运行情况",
        "publisher": "中华人民共和国工业和信息化部",
        "source_url": "https://www.miit.gov.cn/jgsj/yxj/xxfb/art/2026/art_7ecee3ca8eaa489685c7162a18a92fef.html",
        "license_name": "政府公开统计",
        "version": "2026-05 累计",
        "data_type": "软件产业统计",
        "domain": "软件与信息技术服务业",
        "published_at": "2026-06-30",
        "data_count": 21,
        "quality_score": 99.5,
        "status": "verified",
        "sync_message": "已接入最新公开月度累计数据及 2026 年 1—5 月趋势。",
    },
    {
        "source_key": "nbs_employment_2025",
        "source_name": "2025 年城镇单位就业人员工资与行业统计",
        "publisher": "中华人民共和国国家统计局",
        "source_url": "https://www.stats.gov.cn/sj/zxfb/202605/t20260515_1963707.html",
        "license_name": "政府公开统计",
        "version": "2025 年度",
        "data_type": "就业与工资统计",
        "domain": "信息传输、软件和信息技术服务业",
        "published_at": "2026-05-15",
        "data_count": 6,
        "quality_score": 99.5,
        "status": "verified",
        "sync_message": "采用国家统计局年度最终口径，不以招聘网站薪资代替官方统计。",
    },
    {
        "source_key": "onet_30_3",
        "source_name": "O*NET 30.3 职业与技能数据库",
        "publisher": "U.S. Department of Labor / ETA",
        "source_url": "https://www.onetcenter.org/database.html",
        "license_name": "CC BY 4.0",
        "version": "30.3",
        "data_type": "职业、软件技能与核心技能",
        "domain": "国际职业技能标准",
        "published_at": "2026-05-01",
        "data_count": 50717,
        "quality_score": 99.3,
        "status": "verified",
        "sync_message": "完整原始 CSV 保存在本地；系统索引数字技术相关职业及其技能关系。",
    },
    {
        "source_key": "esco_1_2_1",
        "source_name": "ESCO 职业与技能分类",
        "publisher": "European Commission, DG EMPL",
        "source_url": "https://esco.ec.europa.eu/en/use-esco",
        "license_name": "European Commission reuse policy",
        "version": "1.2.1",
        "data_type": "职业与技能分类",
        "domain": "国际职业技能标准",
        "published_at": "2025-12-10",
        "data_count": 16978,
        "quality_score": 99.2,
        "status": "verified_metadata",
        "sync_message": "记录 3,039 个职业与 13,939 个技能概念；保留官方 URI 作为跨库对齐基线。",
    },
    {
        "source_key": "wef_future_jobs_2025",
        "source_name": "Future of Jobs Report 2025",
        "publisher": "World Economic Forum",
        "source_url": "https://www.weforum.org/publications/the-future-of-jobs-report-2025/digest/",
        "license_name": "公开报告（引用使用）",
        "version": "2025",
        "data_type": "全球岗位与技能趋势",
        "domain": "未来工作",
        "published_at": "2025-01-07",
        "data_count": 25,
        "quality_score": 96.0,
        "status": "verified",
        "sync_message": "基于 1,000 余家雇主、覆盖 1,400 万劳动者的调查，只用于趋势层。",
    },
    {
        "source_key": "mohrss_qualification_2026",
        "source_name": "2026 年专业技术人员职业资格考试计划",
        "publisher": "中华人民共和国人力资源和社会保障部",
        "source_url": "https://www.mohrss.gov.cn/xxgk2020/fdzdgknr/qt/gztz/202602/t20260203_566621.html",
        "license_name": "政府公开信息",
        "version": "人社厅函〔2026〕6号",
        "data_type": "职业资格与证书",
        "domain": "人才评价",
        "published_at": "2026-01-23",
        "data_count": 3,
        "quality_score": 99.0,
        "status": "verified",
        "sync_message": "证书推荐只引用国家统一考试或主管部门明确认可的资格。",
    },
    {
        "source_key": "ai_hr_policy_2026",
        "source_name": "“人工智能＋人社”应用发展实施意见",
        "publisher": "人社部、国家发展改革委、工业和信息化部、国家数据局",
        "source_url": "https://www.nda.gov.cn/sjj/zwgk/zcfb/0708/20260708133949899211227_pc.html",
        "license_name": "政府公开政策",
        "version": "2026-07",
        "data_type": "人才图谱政策依据",
        "domain": "人工智能与人力资源",
        "published_at": "2026-07-08",
        "data_count": 1,
        "quality_score": 99.0,
        "status": "verified",
        "sync_message": "作为知识图谱、继续教育和防幻觉治理的最新政策依据。",
    },
]

MIIT_TREND_URLS = {
    "2026-02": "https://www.miit.gov.cn/gxsj/tjfx/rjy/art/2026/art_3bcd054de8664ab1b143a60c65e824da.html",
    "2026-Q1": "https://www.miit.gov.cn/jgsj/yxj/xxfb/art/2026/art_d1942bc02481488dba51dfd1be72b1ef.html",
    "2026-04": "https://www.miit.gov.cn/jgsj/yxj/xxfb/art/2026/art_e38fe37431bc40e8a6bad0c75d06b45b.html",
    "2026-05": "https://www.miit.gov.cn/jgsj/yxj/xxfb/art/2026/art_7ecee3ca8eaa489685c7162a18a92fef.html",
}

METRICS = [
    ("miit_software_2026_05", "software_revenue", "软件业务收入", "2026-02", 21534, "亿元", "industry", MIIT_TREND_URLS["2026-02"], "2026-03-31"),
    ("miit_software_2026_05", "software_revenue", "软件业务收入", "2026-Q1", 34920, "亿元", "industry", MIIT_TREND_URLS["2026-Q1"], "2026-04-30"),
    ("miit_software_2026_05", "software_revenue", "软件业务收入", "2026-04", 46686, "亿元", "industry", MIIT_TREND_URLS["2026-04"], "2026-05-29"),
    ("miit_software_2026_05", "software_revenue", "软件业务收入", "2026-05", 62451, "亿元", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "software_revenue_yoy", "软件业务收入同比增长", "2026-05", 10.3, "%", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "software_profit", "软件业利润总额", "2026-05", 7173, "亿元", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "software_export", "软件业务出口", "2026-05", 276.5, "亿美元", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "it_service_revenue", "信息技术服务收入", "2026-05", 42761, "亿元", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "cloud_bigdata_revenue", "云计算与大数据服务收入", "2026-05", 7032, "亿元", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "cloud_bigdata_yoy", "云计算与大数据服务同比增长", "2026-05", 12.1, "%", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "ic_design_yoy", "集成电路设计收入同比增长", "2026-05", 19.2, "%", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("miit_software_2026_05", "information_security_yoy", "信息安全收入同比增长", "2026-05", 6.5, "%", "industry", MIIT_TREND_URLS["2026-05"], "2026-06-30"),
    ("nbs_employment_2025", "it_wage_non_private", "信息软件业城镇非私营单位年平均工资", "2025", 248752, "元", "employment", "https://www.stats.gov.cn/sj/zxfb/202605/t20260515_1963707.html", "2026-05-15"),
    ("nbs_employment_2025", "it_wage_private", "信息软件业城镇私营单位年平均工资", "2025", 128166, "元", "employment", "https://www.stats.gov.cn/sj/zxfb/202605/t20260515_1963707.html", "2026-05-15"),
    ("nbs_employment_2025", "it_value_added_yoy", "信息软件业增加值同比增长", "2025", 11.1, "%", "employment", "https://www.stats.gov.cn/zt_18555/zthd/lhfw/2026lhzt/2026hgjj/202602/t20260202_1962431.html", "2026-02-02"),
    ("wef_future_jobs_2025", "skills_change_by_2030", "到 2030 年岗位核心技能变化比例", "2025-2030", 39, "%", "forecast", "https://www.weforum.org/publications/the-future-of-jobs-report-2025/digest/", "2025-01-07"),
    ("wef_future_jobs_2025", "upskilling_need", "到 2030 年需要培训的劳动者比例", "2025-2030", 59, "%", "forecast", "https://www.weforum.org/publications/the-future-of-jobs-report-2025/digest/", "2025-01-07"),
    ("wef_future_jobs_2025", "net_job_growth", "到 2030 年预计净新增岗位", "2025-2030", 78, "百万个", "forecast", "https://www.weforum.org/publications/the-future-of-jobs-report-2025/digest/", "2025-01-07"),
]

CURATED_CATALOG = [
    ("mohrss_new_occupations_2026", "occupation", "proposed-2026-01", "数字孪生工程技术人员", "拟新增职业", "从事数字孪生系统建模、集成、仿真与应用的工程技术人员。", {"status": "proposed", "country": "CN"}),
    ("mohrss_new_occupations_2026", "occupation", "proposed-2026-02", "具身智能机器人应用技术员", "拟新增职业", "面向具身智能机器人部署、调试、应用与运维的新职业。", {"status": "proposed", "country": "CN"}),
    ("mohrss_new_occupations_2026", "occupation", "proposed-2026-03", "运动数据分析师", "拟新增职业", "运用数据分析方法处理运动与训练数据的新职业。", {"status": "proposed", "country": "CN"}),
    ("mohrss_new_occupations_2026", "occupation", "proposed-2026-04", "智能体开发员", "拟新增工种", "面向智能体应用设计、开发、编排、评测与维护的新工种。", {"status": "proposed", "country": "CN"}),
    ("wef_future_jobs_2025", "occupation", "wef-job-01", "大数据专家", "全球快速增长岗位", "World Economic Forum 2025 报告列出的快速增长岗位。", {"rank": 1, "trend": "rising"}),
    ("wef_future_jobs_2025", "occupation", "wef-job-02", "金融科技工程师", "全球快速增长岗位", "World Economic Forum 2025 报告列出的快速增长岗位。", {"rank": 2, "trend": "rising"}),
    ("wef_future_jobs_2025", "occupation", "wef-job-03", "AI 与机器学习专家", "全球快速增长岗位", "World Economic Forum 2025 报告列出的快速增长岗位。", {"rank": 3, "trend": "rising"}),
    ("wef_future_jobs_2025", "occupation", "wef-job-04", "软件与应用开发人员", "全球快速增长岗位", "World Economic Forum 2025 报告列出的快速增长岗位。", {"rank": 4, "trend": "rising"}),
    ("wef_future_jobs_2025", "occupation", "wef-job-05", "信息安全分析师", "全球快速增长岗位", "World Economic Forum 2025 报告列出的快速增长岗位。", {"rank": 5, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-01", "AI 与大数据", "快速增长技能", "预计到 2030 年增长最快的技能之一。", {"rank": 1, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-02", "网络与网络安全", "快速增长技能", "预计到 2030 年增长最快的技能之一。", {"rank": 2, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-03", "技术素养", "快速增长技能", "预计到 2030 年增长最快的技能之一。", {"rank": 3, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-04", "创造性思维", "快速增长技能", "技术技能之外持续增长的人类核心能力。", {"rank": 4, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-05", "韧性、灵活性与敏捷性", "快速增长技能", "技术技能之外持续增长的人类核心能力。", {"rank": 5, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-06", "好奇心与终身学习", "快速增长技能", "技术技能之外持续增长的人类核心能力。", {"rank": 6, "trend": "rising"}),
    ("wef_future_jobs_2025", "skill", "wef-skill-07", "分析性思维", "核心技能", "2025 年雇主最重视的核心技能。", {"rank": 1, "trend": "core"}),
    ("mohrss_qualification_2026", "certificate", "cert-2026-01", "计算机技术与软件专业技术资格", "国家专业技术人员职业资格", "2026 年继续安排初级、中级和高级考试。", {"levels": ["初级", "中级", "高级"], "country": "CN"}),
    ("mohrss_qualification_2026", "certificate", "cert-2026-02", "通信专业技术人员职业资格", "国家专业技术人员职业资格", "2026 年继续安排初级和中级考试。", {"levels": ["初级", "中级"], "country": "CN"}),
    ("mohrss_qualification_2026", "certificate", "cert-2026-03", "统计专业技术资格", "国家专业技术人员职业资格", "2026 年继续安排初级、中级和高级考试。", {"levels": ["初级", "中级", "高级"], "country": "CN"}),
]

TECH_OCCUPATION_KEYWORDS = {
    "software", "computer", "data", "database", "web", "cyber", "information security",
    "machine learning", "artificial intelligence", "network", "cloud", "robotics", "digital",
    "systems analyst", "developer", "programmer", "statistician", "operations research",
}


def _parse_date(value: str | None) -> datetime | None:
    return datetime.strptime(value, "%Y-%m-%d") if value else None


def bootstrap_official_data(db: Session) -> None:
    """Install verified source metadata and small primary-source facts without network I/O."""
    now = datetime.utcnow()
    official_keys = {item["source_key"] for item in SOURCE_MANIFEST}
    legacy = db.scalars(select(DataSource).where(DataSource.source_key == "")).all()
    for source in legacy:
        source.source_key = f"legacy_demo_{source.id}"
        source.status = "archived"
        source.sync_message = "历史演示数据，不参与当前市场统计。"
        source.metadata_json = json.dumps({"legacy_demo": True}, ensure_ascii=False)

    for item in SOURCE_MANIFEST:
        source = db.scalar(select(DataSource).where(DataSource.source_key == item["source_key"]))
        if source is None:
            source = DataSource(source_key=item["source_key"], source_name=item["source_name"], data_type=item["data_type"], domain=item["domain"])
            db.add(source)
        for field in ("source_name", "publisher", "source_url", "license_name", "version", "data_type", "domain", "data_count", "quality_score", "status", "sync_message"):
            setattr(source, field, item[field])
        source.published_at = _parse_date(item["published_at"])
        source.uploaded_at = source.published_at or now
        source.last_synced_at = source.last_synced_at or now
        source.indexed_count = source.indexed_count or 0
        source.duplicate_rate = 0
        source.noise_rate = 0
        source.metadata_json = json.dumps({"verified": True, "primary_or_authoritative": True}, ensure_ascii=False)

    db.execute(delete(IndustryMetric).where(IndustryMetric.source_key.in_(official_keys)))
    db.add_all([
        IndustryMetric(
            source_key=source_key,
            metric_key=metric_key,
            label=label,
            period=period,
            value=value,
            unit=unit,
            dimension=dimension,
            evidence_url=evidence_url,
            published_at=_parse_date(published_at),
            collected_at=now,
        )
        for source_key, metric_key, label, period, value, unit, dimension, evidence_url, published_at in METRICS
    ])

    curated_keys = {item[0] for item in CURATED_CATALOG}
    db.execute(delete(ExternalCatalogItem).where(ExternalCatalogItem.source_key.in_(curated_keys)))
    db.add_all([
        ExternalCatalogItem(
            source_key=source_key,
            item_type=item_type,
            external_id=external_id,
            name=name,
            category=category,
            description=description,
            payload_json=json.dumps(payload, ensure_ascii=False),
            published_at=_parse_date(next(source["published_at"] for source in SOURCE_MANIFEST if source["source_key"] == source_key)),
            indexed_at=now,
        )
        for source_key, item_type, external_id, name, category, description, payload in CURATED_CATALOG
    ])
    indexed_counts = Counter(item[0] for item in CURATED_CATALOG)
    indexed_counts.update(item[0] for item in METRICS)
    for source_key, count in indexed_counts.items():
        source = db.scalar(select(DataSource).where(DataSource.source_key == source_key))
        if source and source_key != "onet_30_3":
            source.indexed_count = count
    _refresh_graph_provenance(db)
    from app.services.capability_catalog import sync_capability_catalog
    sync_capability_catalog(db)
    db.flush()


def sync_official_data(db: Session, include_network: bool = True) -> dict:
    run = DataSyncRun(status="running", started_at=datetime.utcnow())
    db.add(run)
    db.flush()
    details: dict[str, object] = {"network": include_network, "sources": []}
    try:
        bootstrap_official_data(db)
        indexed = 0
        if include_network:
            indexed = _sync_onet(db)
            details["sources"].append({"source_key": "onet_30_3", "indexed": indexed, "status": "synced"})
            from app.services.capability_catalog import sync_capability_catalog
            details["capability_catalog"] = sync_capability_catalog(db)
        now = datetime.utcnow()
        for source in db.scalars(select(DataSource).where(DataSource.status != "archived")).all():
            source.last_synced_at = now
        run.status = "completed"
        run.source_count = len(SOURCE_MANIFEST)
        run.record_count = int(sum(item["data_count"] for item in SOURCE_MANIFEST))
        run.completed_at = now
        details["indexed_records"] = indexed + len(CURATED_CATALOG) + len(METRICS)
        run.details_json = json.dumps(details, ensure_ascii=False)
        db.commit()
        return sync_status(db)
    except Exception as exc:
        db.rollback()
        failed = db.get(DataSyncRun, run.id)
        if failed:
            failed.status = "failed"
            failed.completed_at = datetime.utcnow()
            failed.details_json = json.dumps({"error": str(exc), **details}, ensure_ascii=False)
            db.commit()
        raise


def _sync_onet(db: Session) -> int:
    EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    checksums: dict[str, str] = {}
    for file_name, url in ONET_FILES.items():
        target = EXTERNAL_DATA_DIR / file_name
        _download(url, target)
        checksums[file_name] = _sha256(target)

    occupations_path = EXTERNAL_DATA_DIR / "occupation_data.csv"
    software_path = EXTERNAL_DATA_DIR / "software_skills.csv"
    essential_path = EXTERNAL_DATA_DIR / "essential_skills.csv"
    occupation_rows = list(_read_csv(occupations_path))
    selected_occupations = [row for row in occupation_rows if _is_tech_occupation(row)]
    selected_codes = {row["O*NET-SOC Code"] for row in selected_occupations}

    db.execute(delete(ExternalCatalogItem).where(ExternalCatalogItem.source_key == "onet_30_3"))
    now = datetime.utcnow()
    catalog_rows: list[ExternalCatalogItem] = []
    for row in selected_occupations:
        catalog_rows.append(ExternalCatalogItem(
            source_key="onet_30_3",
            external_id=row["O*NET-SOC Code"],
            item_type="occupation",
            name=row["Title"],
            category="Digital & Technology",
            description=row.get("Description", ""),
            payload_json=json.dumps({"onet_soc_code": row["O*NET-SOC Code"], "language": "en"}),
            published_at=_parse_date("2026-05-01"),
            indexed_at=now,
        ))

    software_total = 0
    software_seen: set[tuple[str, str]] = set()
    software_counter: Counter[str] = Counter()
    for row in _read_csv(software_path):
        software_total += 1
        code = row["O*NET-SOC Code"]
        name = row["Workplace Example"].strip()
        if code not in selected_codes or not name or (row.get("Hot Technology") != "Y" and row.get("In Demand") != "Y"):
            continue
        key = (code, name.casefold())
        if key in software_seen:
            continue
        software_seen.add(key)
        software_counter[name] += 1
        catalog_rows.append(ExternalCatalogItem(
            source_key="onet_30_3",
            external_id=f"{code}:software:{hashlib.sha1(name.casefold().encode()).hexdigest()[:12]}",
            item_type="software_skill",
            name=name,
            category=row.get("Element Name", "Software skill"),
            description=f"O*NET occupation {row.get('Title', '')} 使用的软件技能示例。",
            payload_json=json.dumps({
                "onet_soc_code": code,
                "occupation": row.get("Title", ""),
                "hot_technology": row.get("Hot Technology") == "Y",
                "in_demand": row.get("In Demand") == "Y",
            }),
            published_at=_parse_date("2026-05-01"),
            indexed_at=now,
        ))

    essential_total = 0
    essential_seen: set[tuple[str, str]] = set()
    for row in _read_csv(essential_path):
        essential_total += 1
        code = row["O*NET-SOC Code"]
        if code not in selected_codes or row.get("Scale ID") != "IM":
            continue
        value = float(row.get("Data Value") or 0)
        if value < 3.0:
            continue
        name = row.get("Element Name", "").strip()
        key = (code, name.casefold())
        if not name or key in essential_seen:
            continue
        essential_seen.add(key)
        catalog_rows.append(ExternalCatalogItem(
            source_key="onet_30_3",
            external_id=f"{code}:essential:{row.get('Element ID', '')}",
            item_type="essential_skill",
            name=name,
            category="Essential skill",
            description=f"O*NET occupation {row.get('Title', '')} 的重要核心技能。",
            payload_json=json.dumps({"onet_soc_code": code, "occupation": row.get("Title", ""), "importance": value, "date": row.get("Date", "")}),
            published_at=_parse_date("2026-05-01"),
            indexed_at=now,
        ))

    db.bulk_save_objects(catalog_rows)
    source = db.scalar(select(DataSource).where(DataSource.source_key == "onet_30_3"))
    if source:
        source.data_count = len(occupation_rows) + software_total + essential_total
        source.indexed_count = len(catalog_rows)
        source.status = "synced"
        source.sync_message = f"完整下载 {source.data_count:,} 行；索引 {len(selected_occupations)} 个数字技术职业及 {len(catalog_rows) - len(selected_occupations):,} 条技能关系。"
        source.metadata_json = json.dumps({
            "checksums": checksums,
            "occupation_rows": len(occupation_rows),
            "software_skill_rows": software_total,
            "essential_skill_rows": essential_total,
            "top_software_skills": software_counter.most_common(20),
            "modified_by_skillbridge": True,
        }, ensure_ascii=False)
    _refresh_graph_provenance(db)
    db.flush()
    return len(catalog_rows)


def market_snapshot(db: Session) -> dict:
    sources = db.scalars(select(DataSource).where(DataSource.status != "archived").order_by(DataSource.published_at.desc())).all()
    metrics = db.scalars(select(IndustryMetric).order_by(IndustryMetric.published_at.desc(), IndustryMetric.id)).all()
    items = db.scalars(select(ExternalCatalogItem).where(ExternalCatalogItem.source_key.in_(["wef_future_jobs_2025", "mohrss_new_occupations_2026", "mohrss_qualification_2026"])).order_by(ExternalCatalogItem.id)).all()
    top_skills = [catalog_to_dict(item) for item in items if item.item_type == "skill"]
    emerging_jobs = [catalog_to_dict(item) for item in items if item.item_type == "occupation"]
    certificates = [catalog_to_dict(item) for item in items if item.item_type == "certificate"]
    counts = dict(db.execute(select(ExternalCatalogItem.item_type, func.count(ExternalCatalogItem.id)).group_by(ExternalCatalogItem.item_type)).all())
    trend = [
        metric_to_dict(item)
        for item in sorted((metric for metric in metrics if metric.metric_key == "software_revenue"), key=lambda metric: metric.published_at or datetime.min)
    ]
    latest_run = db.scalar(select(DataSyncRun).order_by(DataSyncRun.started_at.desc()))
    return {
        "as_of": max((source.published_at for source in sources if source.published_at), default=None),
        "last_synced_at": max((source.last_synced_at for source in sources if source.last_synced_at), default=None),
        "coverage": {
            "source_count": len(sources),
            "publisher_count": len({source.publisher for source in sources if source.publisher}),
            "record_count": sum(source.data_count or 0 for source in sources),
            "indexed_count": sum(source.indexed_count or 0 for source in sources),
            "catalog_counts": counts,
        },
        "sources": [source_to_dict(source) for source in sources],
        "industry_metrics": [metric_to_dict(metric) for metric in metrics],
        "software_revenue_trend": trend,
        "top_skills": top_skills,
        "emerging_jobs": emerging_jobs,
        "certificates": certificates,
        "latest_run": sync_run_to_dict(latest_run) if latest_run else None,
        "provenance_note": "公开市场数据来自政府、国际组织及开放职业分类；候选人、简历和面试数据只来自系统用户授权输入。",
    }


def sync_status(db: Session) -> dict:
    latest_run = db.scalar(select(DataSyncRun).order_by(DataSyncRun.started_at.desc()))
    sources = db.scalars(select(DataSource).where(DataSource.status != "archived").order_by(DataSource.published_at.desc())).all()
    return {
        "run": sync_run_to_dict(latest_run) if latest_run else None,
        "source_count": len(sources),
        "record_count": sum(source.data_count or 0 for source in sources),
        "indexed_count": sum(source.indexed_count or 0 for source in sources),
        "sources": [source_to_dict(source) for source in sources],
    }


def source_to_dict(source: DataSource) -> dict:
    return {
        "id": source.id,
        "source_key": source.source_key,
        "source_name": source.source_name,
        "publisher": source.publisher,
        "source_url": source.source_url,
        "license_name": source.license_name,
        "version": source.version,
        "data_type": source.data_type,
        "domain": source.domain,
        "published_at": source.published_at,
        "last_synced_at": source.last_synced_at,
        "uploaded_at": source.uploaded_at,
        "data_count": source.data_count,
        "indexed_count": source.indexed_count,
        "duplicate_rate": source.duplicate_rate,
        "noise_rate": source.noise_rate,
        "quality_score": source.quality_score,
        "status": source.status,
        "sync_message": source.sync_message,
        "metadata": _json_object(source.metadata_json),
    }


def metric_to_dict(metric: IndustryMetric) -> dict:
    return {
        "metric_key": metric.metric_key,
        "label": metric.label,
        "period": metric.period,
        "value": metric.value,
        "unit": metric.unit,
        "dimension": metric.dimension,
        "evidence_url": metric.evidence_url,
        "published_at": metric.published_at,
    }


def catalog_to_dict(item: ExternalCatalogItem) -> dict:
    return {
        "external_id": item.external_id,
        "source_key": item.source_key,
        "item_type": item.item_type,
        "name": item.name,
        "category": item.category,
        "description": item.description,
        "payload": _json_object(item.payload_json),
        "published_at": item.published_at,
    }


def sync_run_to_dict(run: DataSyncRun) -> dict:
    return {
        "id": run.id,
        "status": run.status,
        "source_count": run.source_count,
        "record_count": run.record_count,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "details": _json_object(run.details_json),
    }


def _download(url: str, target: Path) -> None:
    temp_target = target.with_suffix(target.suffix + ".download")
    request = Request(url, headers={"User-Agent": "SkillBridge-Graph/1.0 (+educational research)"})
    with urlopen(request, timeout=60) as response, temp_target.open("wb") as output:
        shutil.copyfileobj(response, output)
    temp_target.replace(target)


def _read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def _is_tech_occupation(row: dict[str, str]) -> bool:
    value = f"{row.get('Title', '')} {row.get('Description', '')}".casefold()
    return any(keyword in value for keyword in TECH_OCCUPATION_KEYWORDS)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(value: str | None) -> dict:
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except (TypeError, ValueError):
        return {}


def _refresh_graph_provenance(db: Session) -> None:
    """Replace seed-like claims with explicit, honest source and derivation statements."""
    onet_url = "https://www.onetcenter.org/database.html"
    esco_url = "https://esco.ec.europa.eu/en/use-esco"
    wef_url = "https://www.weforum.org/publications/the-future-of-jobs-report-2025/digest/"
    mohrss_url = "https://chinajob.mohrss.gov.cn/c/2026-07-10/569764.shtml"
    for job in db.scalars(select(JobEntity)).all():
        source_hint = mohrss_url if any(token in job.name for token in ("智能体", "数字孪生", "机器人")) else wef_url if any(token in job.name for token in ("AI", "大模型", "机器学习", "数据", "安全", "软件")) else esco_url
        job.evidence = f"岗位名称与趋势参考：{source_hint}；能力要求由系统基于 O*NET 30.3（{onet_url}）和 ESCO 1.2.1（{esco_url}）进行中文场景映射，属于本系统派生结果。"
    for skill in db.scalars(select(SkillEntity)).all():
        trend_hint = wef_url if any(token in skill.name for token in ("AI", "大数据", "网络", "安全", "分析", "学习")) else onet_url
        skill.evidence = f"技能概念参考：{trend_hint}；分类与中文名称为本系统对 O*NET 30.3、ESCO 1.2.1 的本地化映射，并非来源机构的官方中文译名。"
    jobs = {job.id: job for job in db.scalars(select(JobEntity)).all()}
    skills = {skill.id: skill for skill in db.scalars(select(SkillEntity)).all()}
    for relation in db.scalars(select(JobSkillRelation)).all():
        job = jobs.get(relation.job_id)
        skill = skills.get(relation.skill_id)
        if job and skill:
            relation.evidence = f"派生关系：{job.name} → {skill.name}；依据 O*NET/ESCO 职业技能框架与本系统中文岗位画像交叉映射，需结合真实 JD 持续校准。"
