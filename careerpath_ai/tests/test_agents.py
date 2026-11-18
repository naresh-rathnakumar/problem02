"""
Unit tests for multi-agent logic and structured outputs.
"""

from agents.resume_agent import ResumeAnalysisAgent
from agents.job_matching_agent import JobMatchingAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.recommendation_agent import RecommendationAgent


def test_agent_initialization():
    r_agent = ResumeAnalysisAgent()
    assert r_agent.name == "Resume Analysis Agent"

    j_agent = JobMatchingAgent()
    assert j_agent.name == "Job Matching Agent"

    g_agent = SkillGapAgent()
    assert g_agent.name == "Skill Gap Analysis Agent"

    rc_agent = RecommendationAgent()
    assert rc_agent.name == "Career Recommendation & Roadmap Agent"


def test_resume_agent_deterministic_extraction():
    agent = ResumeAnalysisAgent()
    sample_text = """
    Alex Rivera
    alex@example.com
    Skills: Python, SQL, Pandas, PyTorch, Docker, Git
    Project: Built an AI Search Engine with FastAPI and PostgreSQL
    """
    profile = agent.analyze(sample_text)
    assert profile["candidate_name"] == "Alex Rivera"
    assert profile["email"] == "alex@example.com"
    langs = [l.lower() for l in profile["programming_languages"]]
    assert "python" in langs
    assert "sql" in langs


def test_job_matching_deterministic():
    agent = JobMatchingAgent()
    profile = {
        "candidate_name": "Alex Rivera",
        "programming_languages": ["Python", "SQL"],
        "frameworks_libraries": ["Pandas", "Scikit-learn"],
        "tools_platforms": ["Git"],
        "databases": ["PostgreSQL"],
        "total_experience_years": 2.0,
        "projects": [{"name": "ML Project", "technologies": ["Python", "Scikit-learn"]}]
    }
    jd = """
    Role: Python Developer
    Required: Python, SQL, FastAPI, Docker
    Preferred: AWS, Redis
    """
    match = agent.match(profile, jd, "Python Developer")
    assert match["job_title"] == "Python Developer"
    assert match["overall_score"] > 0
    assert "Python" in [s["skill"] for s in match["matched_skills"] if s["matched"]]
