"""
Unit tests for transparent weighted scoring algorithm.
"""

from core.scoring import ScoringEngine


def test_scoring_weights_normalized():
    engine = ScoringEngine()
    total = sum(engine.weights.values())
    assert abs(total - 1.0) < 0.001


def test_calculate_required_skills_score():
    engine = ScoringEngine()
    required = ["Python", "FastAPI", "Docker", "PostgreSQL"]
    candidate = ["python", "postgresql", "git", "bash"]

    score, matched, missing = engine.calculate_required_skills_score(required, candidate)
    assert score == 50.0
    assert "Python" in matched
    assert "PostgreSQL" in matched
    assert "Docker" in missing
    assert "FastAPI" in missing


def test_skill_variant_matching():
    engine = ScoringEngine()
    required = ["Kubernetes", "Scikit-Learn"]
    candidate = ["k8s", "sklearn"]

    score, matched, missing = engine.calculate_required_skills_score(required, candidate)
    assert score == 100.0
    assert len(missing) == 0


def test_overall_weighted_score():
    engine = ScoringEngine()
    overall = engine.calculate_overall_score(
        required_skills_score=80.0,
        preferred_skills_score=50.0,
        project_evidence_score=75.0,
        education_experience_score=100.0
    )
    # 80*0.5 + 50*0.2 + 75*0.2 + 100*0.1 = 40 + 10 + 15 + 10 = 75.0
    assert overall == 75.0
