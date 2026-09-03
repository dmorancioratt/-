from app.services.matching import rank_job_profiles, score_match


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


def test_rank_job_profiles_prefers_specific_frontend_evidence():
    candidate = {
        "skills": ["JavaScript", "TypeScript", "Vue", "ECharts", "响应式布局"],
        "projects": ["负责 Vue 和 TypeScript 数据可视化后台，优化首屏加载 35%"],
    }
    jobs = [
        {
            "name": "前端开发工程师",
            "domain": "软件研发",
            "description": "负责 Web 前端、Vue、TypeScript 和 ECharts 可视化页面开发",
            "required_skills": ["Vue", "TypeScript", "ECharts"],
            "preferred_skills": ["数据可视化"],
        },
        {
            "name": "全栈开发工程师",
            "domain": "软件研发",
            "description": "负责前后端业务系统、Node.js 和数据库服务开发",
            "required_skills": ["JavaScript", "Node.js", "SQL"],
            "preferred_skills": ["Docker"],
        },
    ]
    ranking = rank_job_profiles(candidate, jobs)
    assert ranking[0]["job_name"] == "前端开发工程师"
    assert ranking[0]["required_skill_score"] > ranking[1]["required_skill_score"]
