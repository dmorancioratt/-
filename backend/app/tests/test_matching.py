from app.services.matching import score_match


def test_evidence_changes_project_and_scenario_scores():
    base = score_match(
        ["Python"],
        ["Python", "RAG", "Docker"],
        ["Kubernetes"],
        [],
        job_name="AI 应用开发工程师",
        job_description="负责企业知识库、RAG 服务开发与容器化部署",
        job_domain="人工智能",
    )
    rich = score_match(
        ["Python", "RAG", "Docker", "K8s"],
        ["Python", "RAG", "Docker"],
        ["Kubernetes"],
        ["人工智能工程师认证"],
        projects=["负责企业 RAG 知识库，使用 Python 和 Docker 部署，上线后问答命中率提升 18%"],
        internships=["参与 AI 平台服务开发与业务需求分析"],
        job_name="AI 应用开发工程师",
        job_description="负责企业知识库、RAG 服务开发与容器化部署",
        job_domain="人工智能",
    )

    assert rich["total_score"] > base["total_score"]
    assert rich["project_score"] > base["project_score"]
    assert rich["scenario_score"] > base["scenario_score"]
    assert "Kubernetes" in rich["matched_skills"]
    assert rich["missing_skills"] == []


def test_each_dimension_contains_explainable_evidence_shape():
    report = score_match(
        ["SQL"],
        ["SQL", "Python"],
        ["Docker"],
        projects=["使用 SQL 完成数据清洗与报表开发"],
    )

    assert len(report["dimension_rows"]) == 6
    assert all({"name", "score", "weight", "summary", "matched", "missing", "evidence"} <= set(row) for row in report["dimension_rows"])
    assert sum(row["weight"] for row in report["dimension_rows"]) == 100
    assert report["scoring_version"] == "evidence-v2"
