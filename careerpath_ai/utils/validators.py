"""
Validation helpers for agent inputs, outputs, and structured data schemas.
"""

from typing import Dict, Any, List


def validate_resume_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required fields exist in resume analysis dictionary."""
    defaults = {
        "candidate_name": "Candidate",
        "email": "",
        "phone": "",
        "location": "",
        "summary": "",
        "technical_skills": [],
        "soft_skills": [],
        "programming_languages": [],
        "frameworks_libraries": [],
        "tools_platforms": [],
        "databases": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "total_experience_years": 0.0,
        "raw_text": "",
    }
    for k, v in defaults.items():
        if k not in data or data[k] is None:
            data[k] = v
    return data


def validate_match_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure standard structure for job matching outcome."""
    defaults = {
        "job_title": "Target Role",
        "overall_score": 0.0,
        "required_skills_score": 0.0,
        "preferred_skills_score": 0.0,
        "project_evidence_score": 0.0,
        "education_experience_score": 0.0,
        "matched_skills": [],
        "missing_skills": [],
        "matching_reasons": [],
        "improvement_areas": [],
        "suitability": "",
    }
    for k, v in defaults.items():
        if k not in data or data[k] is None:
            data[k] = v
    return data


def validate_skill_gap(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure standard structure for skill gap analysis."""
    defaults = {
        "job_title": "Target Role",
        "strongly_demonstrated": [],
        "under_evidenced": [],
        "not_evidenced": [],
        "total_required_skills": 0,
        "coverage_percentage": 0.0,
        "critical_gaps": [],
        "summary": "",
    }
    for k, v in defaults.items():
        if k not in data or data[k] is None:
            data[k] = v
    return data
