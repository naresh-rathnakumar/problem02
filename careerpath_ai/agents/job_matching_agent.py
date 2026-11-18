"""
Agent 2: Job Description Matching Agent
Compares candidate profile with multiple job descriptions using
transparent, weighted mathematical scoring criteria.
"""

import time
import json
from typing import Dict, Any, List
from core.ollama_client import OllamaClient
from core.prompts import JOB_MATCHING_PROMPT
from core.scoring import ScoringEngine
from utils.skill_extractor import get_all_candidate_skills, extract_skills_nlp
from utils.validators import validate_match_result


class JobMatchingAgent:
    """Specialized Agent 2: Matches candidate profile to target job descriptions."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.name = "Job Matching Agent"
        self.ollama = ollama_client or OllamaClient()
        self.scoring = ScoringEngine()
        self.system_prompt = JOB_MATCHING_PROMPT

    def match(self, resume_analysis: Dict[str, Any], job_description: str, job_title: str = "") -> Dict[str, Any]:
        """Perform explainable, weighted match calculation between candidate and job description."""
        start_time = time.time()
        candidate_skills = get_all_candidate_skills(resume_analysis)

        # 1. Ask Local LLM to extract requirements & analyze context
        user_prompt = f"""Compare the Candidate Profile against this Job Description.
Target Job Title: {job_title or 'Detect from text'}

CANDIDATE PROFILE SUMMARY:
- Name: {resume_analysis.get('candidate_name')}
- Programming Languages: {', '.join(resume_analysis.get('programming_languages', []))}
- Frameworks & Libraries: {', '.join(resume_analysis.get('frameworks_libraries', []))}
- Tools & Platforms: {', '.join(resume_analysis.get('tools_platforms', []))}
- Databases: {', '.join(resume_analysis.get('databases', []))}
- Projects: {json.dumps([p.get('name') for p in resume_analysis.get('projects', []) if isinstance(p, dict)])}
- Experience (Years): {resume_analysis.get('total_experience_years', 0)}

JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON matching the schema.
"""
        llm_data = {}
        try:
            llm_data = self.ollama.invoke_json(self.system_prompt, user_prompt)
        except Exception:
            # Deterministic requirement extraction if LLM is offline
            llm_data = self._deterministic_jd_extract(job_description, job_title)

        effective_title = job_title or llm_data.get("job_title", "Engineering Role")
        required_skills = llm_data.get("required_skills", [])
        preferred_skills = llm_data.get("preferred_skills", [])

        # Fallback if LLM returned empty lists
        if not required_skills:
            nlp_jd = extract_skills_nlp(job_description)
            required_skills = (
                nlp_jd.get("programming_languages", [])
                + nlp_jd.get("frameworks", [])[:3]
                + nlp_jd.get("databases", [])[:2]
            )
            preferred_skills = nlp_jd.get("tools_platforms", [])[:3]

        # 2. Deterministic scoring through transparent scoring engine
        req_score, req_matched, req_missing = self.scoring.calculate_required_skills_score(
            required_skills, candidate_skills
        )
        pref_score, pref_matched, pref_missing = self.scoring.calculate_preferred_skills_score(
            preferred_skills, candidate_skills
        )
        proj_score = self.scoring.calculate_project_evidence_score(
            required_skills,
            resume_analysis.get("projects", []),
            resume_analysis.get("experience", [])
        )
        edu_score = self.scoring.calculate_education_experience_score(
            float(llm_data.get("required_experience_years", 2.0)),
            float(resume_analysis.get("total_experience_years", 1.0)),
            llm_data.get("education_requirements", []),
            resume_analysis.get("education", [])
        )

        overall_score = self.scoring.calculate_overall_score(
            req_score, pref_score, proj_score, edu_score
        )

        # 3. Assemble detailed matched skills with evidence
        matched_skills_list = []
        for sk in required_skills:
            is_m = sk in req_matched
            evidence = "Not Evidenced in Resume"
            if is_m:
                # Find matching context from candidate skills
                for item in resume_analysis.get("technical_skills", []):
                    if isinstance(item, dict) and item.get("name", "").lower() == sk.lower():
                        evidence = item.get("context", "Verified in profile")
                        break
                else:
                    evidence = "Demonstrated in candidate background"

            matched_skills_list.append({
                "skill": sk,
                "matched": is_m,
                "evidence": evidence,
                "is_required": True
            })

        for sk in preferred_skills:
            is_m = sk in pref_matched
            evidence = "Demonstrated in candidate background" if is_m else "Not Evidenced in Resume"
            matched_skills_list.append({
                "skill": sk,
                "matched": is_m,
                "evidence": evidence,
                "is_required": False
            })

        # Assemble matching reasons and suitability
        reasons = llm_data.get("matching_reasons") or [
            f"Candidate matches {len(req_matched)} of {len(required_skills)} required technical competencies."
        ]
        improvement_areas = llm_data.get("improvement_areas") or [
            f"Gaps identified in required stack: {', '.join(req_missing[:3]) if req_missing else 'None'}."
        ]
        suitability = llm_data.get("suitability") or (
            f"Candidate demonstrates {overall_score:.1f}% weighted compatibility for {effective_title}. "
            f"Primary strengths in {', '.join(req_matched[:3]) if req_matched else 'general foundations'}."
        )

        result = {
            "job_title": effective_title,
            "overall_score": overall_score,
            "required_skills_score": round(req_score, 1),
            "preferred_skills_score": round(pref_score, 1),
            "project_evidence_score": round(proj_score, 1),
            "education_experience_score": round(edu_score, 1),
            "matched_skills": matched_skills_list,
            "missing_skills": sorted(list(set(req_missing + pref_missing))),
            "matching_reasons": reasons,
            "improvement_areas": improvement_areas,
            "suitability": suitability,
            "_execution_time": round(time.time() - start_time, 2),
            "_agent": self.name
        }

        return validate_match_result(result)

    def match_multiple(self, resume_analysis: Dict[str, Any], job_descriptions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Match candidate against multiple roles and rank in descending order of compatibility."""
        results = []
        for jd_entry in job_descriptions:
            title = jd_entry.get("title", "")
            desc = jd_entry.get("description", "")
            m = self.match(resume_analysis, desc, title)
            results.append(m)

        # Rank by overall compatibility score descending
        results.sort(key=lambda x: x.get("overall_score", 0.0), reverse=True)
        return results

    def _deterministic_jd_extract(self, jd_text: str, title: str) -> Dict[str, Any]:
        """Extract JD requirements deterministically when Ollama is offline."""
        nlp = extract_skills_nlp(jd_text)
        required = (
            nlp.get("programming_languages", [])
            + nlp.get("frameworks", [])[:3]
            + nlp.get("databases", [])[:2]
        )
        preferred = nlp.get("tools_platforms", [])[:3]

        return {
            "job_title": title or "Engineering Position",
            "required_skills": required,
            "preferred_skills": preferred,
            "required_experience_years": 2.0,
            "education_requirements": ["Bachelor's degree in relevant discipline"],
            "matching_reasons": ["Automated skill taxonomy parsing performed."],
            "improvement_areas": ["Identified missing skills across target architecture."],
            "suitability": f"Automated analysis indicates active compatibility with {title} requirements."
        }
