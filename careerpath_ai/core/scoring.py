"""
Transparent, weighted scoring system for job matching.
All weights are configurable via .env file.
"""

import os
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv

load_dotenv()


class ScoringEngine:
    """Transparent job matching scoring engine with configurable weights."""

    def __init__(self):
        self.weights = {
            "required_technical": float(os.getenv("WEIGHT_REQUIRED_TECHNICAL", "0.50")),
            "preferred_technical": float(os.getenv("WEIGHT_PREFERRED_TECHNICAL", "0.20")),
            "project_evidence": float(os.getenv("WEIGHT_PROJECT_EVIDENCE", "0.20")),
            "education_experience": float(os.getenv("WEIGHT_EDUCATION_EXPERIENCE", "0.10")),
        }
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def get_weights_display(self) -> Dict[str, str]:
        return {k: f"{v*100:.0f}%" for k, v in self.weights.items()}

    def calculate_required_skills_score(
        self, required_skills: List[str], candidate_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        if not required_skills:
            return 100.0, [], []
        candidate_lower = [s.lower().strip() for s in candidate_skills]
        matched, missing = [], []
        for skill in required_skills:
            skill_l = skill.lower().strip()
            found = any(skill_l in cs or cs in skill_l for cs in candidate_lower)
            if not found:
                variants = self._get_skill_variants(skill_l)
                found = any(v in cs or cs in v for cs in candidate_lower for v in variants)
            if found:
                matched.append(skill)
            else:
                missing.append(skill)
        score = (len(matched) / len(required_skills)) * 100
        return score, matched, missing

    def calculate_preferred_skills_score(
        self, preferred_skills: List[str], candidate_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        if not preferred_skills:
            return 100.0, [], []
        return self.calculate_required_skills_score(preferred_skills, candidate_skills)

    def calculate_project_evidence_score(
        self, required_skills: List[str], projects: List[Dict], experience: List[Dict]
    ) -> float:
        if not required_skills:
            return 100.0
        evidenced = set()
        for item in projects + experience:
            if isinstance(item, dict):
                for t in item.get("technologies", []):
                    evidenced.add(t.lower().strip())
                desc = item.get("description", "").lower()
                for skill in required_skills:
                    if skill.lower() in desc:
                        evidenced.add(skill.lower().strip())
        matches = 0
        for skill in required_skills:
            skill_l = skill.lower().strip()
            if any(skill_l in es or es in skill_l for es in evidenced):
                matches += 1
            else:
                variants = self._get_skill_variants(skill_l)
                if any(v in es or es in v for es in evidenced for v in variants):
                    matches += 1
        return (matches / len(required_skills)) * 100

    def calculate_education_experience_score(
        self, required_exp_years: float, candidate_exp_years: float,
        education_requirements: List[str], candidate_education: List[Dict]
    ) -> float:
        if required_exp_years <= 0:
            exp_score = 100.0
        elif candidate_exp_years >= required_exp_years:
            exp_score = 100.0
        elif candidate_exp_years > 0:
            exp_score = (candidate_exp_years / required_exp_years) * 100
        else:
            exp_score = 30.0

        if not education_requirements:
            edu_score = 100.0
        else:
            edu_keywords = []
            for req in education_requirements:
                edu_keywords.extend(req.lower().split())
            edu_score = 0.0
            for edu in candidate_education:
                if isinstance(edu, dict):
                    combined = f"{edu.get('degree', '')} {edu.get('field', '')}".lower()
                    matches_count = sum(1 for kw in edu_keywords if kw in combined)
                    if matches_count > 0:
                        edu_score = min(100.0, (matches_count / max(len(edu_keywords), 1)) * 100)
                        break
            if edu_score == 0 and candidate_education:
                edu_score = 50.0

        return exp_score * 0.5 + edu_score * 0.5

    def calculate_overall_score(
        self, required_skills_score: float, preferred_skills_score: float,
        project_evidence_score: float, education_experience_score: float
    ) -> float:
        score = (
            required_skills_score * self.weights["required_technical"]
            + preferred_skills_score * self.weights["preferred_technical"]
            + project_evidence_score * self.weights["project_evidence"]
            + education_experience_score * self.weights["education_experience"]
        )
        return round(score, 1)

    def _get_skill_variants(self, skill: str) -> List[str]:
        variants_map = {
            "javascript": ["js", "es6", "ecmascript"],
            "typescript": ["ts"],
            "python": ["py", "python3"],
            "machine learning": ["ml", "machine-learning"],
            "deep learning": ["dl", "deep-learning"],
            "artificial intelligence": ["ai"],
            "natural language processing": ["nlp"],
            "computer vision": ["cv"],
            "amazon web services": ["aws"],
            "google cloud platform": ["gcp"],
            "microsoft azure": ["azure"],
            "postgresql": ["postgres", "psql"],
            "mongodb": ["mongo"],
            "kubernetes": ["k8s"],
            "docker": ["containerization"],
            "continuous integration": ["ci", "ci/cd"],
            "react": ["reactjs", "react.js"],
            "angular": ["angularjs"],
            "vue": ["vuejs", "vue.js"],
            "node": ["nodejs", "node.js"],
            "tensorflow": ["tf"],
            "pytorch": ["torch"],
            "scikit-learn": ["sklearn", "scikit"],
            "pandas": ["pd"],
            "numpy": ["np"],
            "rest api": ["restful", "rest", "rest apis"],
            "sql": ["structured query language"],
            "html": ["html5"],
            "css": ["css3"],
            "git": ["github", "gitlab", "version control"],
            "agile": ["scrum", "kanban"],
            "devops": ["dev-ops"],
            "data science": ["data-science"],
        }
        result = []
        for key, vals in variants_map.items():
            if skill == key:
                result.extend(vals)
            elif skill in vals:
                result.append(key)
                result.extend([v for v in vals if v != skill])
        return result

    def get_methodology_description(self) -> str:
        return f"""### Transparent Scoring Methodology

The match score is deterministically calculated using a weighted formula:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Required Technical Skills** | {self.weights['required_technical']*100:.0f}% | Percentage of required skills evidenced in resume |
| **Preferred Technical Skills** | {self.weights['preferred_technical']*100:.0f}% | Percentage of preferred skills evidenced in resume |
| **Project / Work Evidence** | {self.weights['project_evidence']*100:.0f}% | Skills directly validated in projects or experience |
| **Education & Experience** | {self.weights['education_experience']*100:.0f}% | Alignment with minimum years and degree field |

**Overall Compatibility Score** = Σ (Component Score × Component Weight)

Match logic uses exact term analysis and standardized variant aliasing (e.g. `k8s` ↔ `kubernetes`, `sklearn` ↔ `scikit-learn`).
"""
