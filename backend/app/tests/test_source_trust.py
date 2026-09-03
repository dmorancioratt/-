from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models import DataSource, RawJD
from app.services.jd_parser import text_hash
from app.services.source_trust import (
    plagiarism_similarity,
    time_decay_weight,
    validate_source_trust,
)


def _source(name: str, key: str, now: datetime) -> DataSource:
    return DataSource(
        source_key=key,
        source_name=name,
        publisher=name,
        source_url=f"https://example.com/{key}",
        license_name="公开招聘信息研究使用",
        data_type="真实岗位 JD",
        domain="软件研发",
        published_at=now,
        last_synced_at=now,
        uploaded_at=now,
        data_count=2,
        indexed_count=2,
        status="imported",
        metadata_json='{"verified": true}',
    )


def test_source_validation_filters_noise_detects_plagiarism_and_normalizes_weights():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    now = datetime(2026, 9, 1, 12, 0, 0)
    base = (
        "负责企业知识库检索增强系统研发，完成文档解析、向量检索、重排序和答案引用校验。"
        "要求熟悉 Python、FastAPI、向量数据库、RAG 评测方法，能够编写自动化测试并分析线上指标。"
        "候选人需要参与需求评审、系统设计、性能优化和上线复盘，提交可追溯的项目成果与技术文档。"
    )
    copied = base.replace("企业知识库", "行业知识库").replace("Python", "Python 3")

    with Session() as db:
        first = _source("招聘源 A", "source-a", now)
        second = _source("招聘源 B", "source-b", now - timedelta(days=180))
        db.add_all([first, second])
        db.flush()
        rows = [
            RawJD(source_id=first.id, title="RAG 工程师", content=base, text_hash=text_hash(base), published_at=now),
            RawJD(source_id=first.id, title="后端工程师", content=base + "负责服务监控和容器部署。", text_hash=text_hash(base + "部署"), published_at=now),
            RawJD(source_id=second.id, title="知识库工程师", content=copied, text_hash=text_hash(copied), published_at=now - timedelta(days=180)),
            RawJD(source_id=second.id, title="高薪职位", content="加微信，高薪日结，无门槛。", text_hash=text_hash("noise"), published_at=now),
        ]
        db.add_all(rows)
        db.commit()

        report = validate_source_trust(db, now=now)

        assert report["summary"]["plagiarism_count"] >= 1
        assert report["summary"]["noise_count"] == 1
        assert report["summary"]["plagiarism_recall"] == 1.0
        assert abs(sum(source["weight"] for source in report["sources"]) - 1.0) < 1e-5
        assert rows[2].is_duplicate is True
        assert rows[2].parse_status == "filtered_duplicate"
        assert rows[3].parse_status == "filtered_noise"
        source_b = next(source for source in report["sources"] if source["source_key"] == "source-b")
        assert source_b["time_decay_weight"] == 0.5
        assert source_b["trust_score"] < next(source for source in report["sources"] if source["source_key"] == "source-a")["trust_score"]


def test_plagiarism_similarity_distinguishes_copies_from_unrelated_text():
    original = "数据工程师负责实时数仓建设、数据质量治理、指标口径维护和任务性能优化。" * 4
    copied = original.replace("实时数仓", "流式数仓").replace("性能优化", "效率优化")
    unrelated = "产品经理负责用户访谈、需求分析、原型设计、版本规划和跨团队沟通。" * 4

    assert plagiarism_similarity(original, copied) >= 0.82
    assert plagiarism_similarity(original, unrelated) < 0.82
    assert time_decay_weight(datetime(2026, 3, 5), now=datetime(2026, 9, 1)) == 0.5
