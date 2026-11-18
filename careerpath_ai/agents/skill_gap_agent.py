"""
Agent 3: Skill Gap Analysis Agent
Performs nuanced gap analysis, categorizes evidence levels,
assigns High/Medium/Low priorities, and identifies improvable projects.
Strictly adheres to 'Not evidenced in resume' terminology.
"""

import time
import json
from typing import Dict, Any, List
from core.ollama_client import OllamaClient
from core.prompts import SKILL_GAP_PROMPT
from utils.validators import validate_skill_gap


class SkillGapAgent:
    """Specialized Agent 3: Detailed gap analysis and actionable project improvement ideas."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.name = "Skill Gap Analysis Agent"
        self.ollama = ollama_client or OllamaClient()
        self.system_prompt = SKILL_GAP_PROMPT

    def analyze(self, resume_analysis: Dict[str, Any], match_result: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Categorize skills into strongly demonstrated, under-evidenced, and not evidenced in resume."""
        start_time = time.time()
        job_title = match_result.get("job_title", "Target Role")
        candidate_projects = [
            p.get("name", "") for p in resume_analysis.get("projects", []) if isinstance(p, dict)
        ]

        user_prompt = f"""Perform a comprehensive Skill Gap Analysis.
Target Role: {job_title}
Match Score: {match_result.get('overall_score')}%

MATCHED SKILLS:
{json.dumps(match_result.get('matched_skills', []))}

MISSING SKILLS:
{json.dumps(match_result.get('missing_skills', []))}

CANDIDATE PROJECTS:
{json.dumps(candidate_projects)}

JOB DESCRIPTION:
{job_description}

REMEMBER: Label missing skills as "Not evidenced in resume". Never say the candidate lacks a skill.
Assign priorities (High, Medium, Low) and identify which candidate projects could be upgraded.
Return ONLY valid JSON.
"""
        llm_data = {}
        try:
            llm_data = self.ollama.invoke_json(self.system_prompt, user_prompt)
        except Exception:
            llm_data = self._deterministic_gap_analysis(resume_analysis, match_result, candidate_projects)

        # Enrich and ensure strict gap compliance
        final_gaps = self._enforce_gap_contracts(llm_data, match_result, candidate_projects, job_title)
        final_gaps = validate_skill_gap(final_gaps)

        final_gaps["_execution_time"] = round(time.time() - start_time, 2)
        final_gaps["_agent"] = self.name
        return final_gaps

    def analyze_multiple(self, resume_analysis: Dict[str, Any], match_results: List[Dict[str, Any]], job_descriptions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Analyze gaps across multiple roles."""
        jd_map = {jd.get("title", ""): jd.get("description", "") for jd in job_descriptions}
        results = []
        for m in match_results:
            title = m.get("job_title", "")
            desc = jd_map.get(title, "")
            gap_data = self.analyze(resume_analysis, m, desc)
            results.append(gap_data)
        return results

    def _enforce_gap_contracts(self, data: Dict[str, Any], match_result: Dict[str, Any], candidate_projects: List[str], job_title: str) -> Dict[str, Any]:
        """Guarantee every missing skill from matching agent is explicitly represented in not_evidenced."""
        strongly_demonstrated = data.get("strongly_demonstrated", [])
        under_evidenced = data.get("under_evidenced", [])
        not_evidenced = data.get("not_evidenced", [])

        existing_missing_names = {
            item.get("skill", "").lower() for item in not_evidenced if isinstance(item, dict)
        }

        # Make sure every missing skill from match_result is registered
        for miss in match_result.get("missing_skills", []):
            if miss.lower() not in existing_missing_names:
                not_evidenced.append({
                    "skill": miss,
                    "category": "Technical",
                    "current_evidence": "Not evidenced in resume",
                    "job_requirement": "Required",
                    "priority": "High" if len(not_evidenced) < 3 else "Medium",
                    "importance_reason": f"Essential capability required for {job_title} production deliverables.",
                    "recommendation": f"Acquire competency in {miss} via practical hands-on mini-projects and documentation study.",
                    "improvable_projects": candidate_projects[:2] if candidate_projects else ["Core Portfolio Project"]
                })

        total_skills = len(strongly_demonstrated) + len(under_evidenced) + len(not_evidenced)
        coverage = 0.0
        if total_skills > 0:
            coverage = ((len(strongly_demonstrated) + (len(under_evidenced) * 0.5)) / total_skills) * 100.0

        critical = data.get("critical_gaps", [])
        if not critical:
            critical = [
                i.get("skill") for i in not_evidenced
                if isinstance(i, dict) and i.get("priority") == "High"
            ][:4]

        return {
            "job_title": job_title,
            "strongly_demonstrated": strongly_demonstrated,
            "under_evidenced": under_evidenced,
            "not_evidenced": not_evidenced,
            "total_required_skills": total_skills,
            "coverage_percentage": round(coverage, 1),
            "critical_gaps": critical,
            "summary": data.get("summary") or f"Analysis for {job_title}: {len(strongly_demonstrated)} strong competencies, {len(not_evidenced)} gaps identified."
        }

    def _deterministic_gap_analysis(self, resume: Dict[str, Any], match: Dict[str, Any], projects: List[str]) -> Dict[str, Any]:
        """Deterministic gap fallback logic."""
        strongly = []
        for m in match.get("matched_skills", []):
            if m.get("matched"):
                strongly.append({
                    "skill": m.get("skill"),
                    "category": "Technical",
                    "current_evidence": m.get("evidence", "Evidenced in profile"),
                    "job_requirement": "Required" if m.get("is_required") else "Preferred",
                    "priority": "High" if m.get("is_required") else "Medium",
                    "importance_reason": "Core required competency aligned with role specifications.",
                    "recommendation": "Deepen advanced optimization and architectural mastery.",
                    "improvable_projects": projects[:1]
                })

        not_ev = []
        for miss in match.get("missing_skills", []):
            not_ev.append({
                "skill": miss,
                "category": "Technical",
                "current_evidence": "Not evidenced in resume",
                "job_requirement": "Required",
                "priority": "High" if len(not_ev) < 3 else "Medium",
                "importance_reason": f"Expected standard proficiency for this position.",
                "recommendation": f"Build practical implementations leveraging {miss}.",
                "improvable_projects": projects[:2]
            })

        return {
            "job_title": match.get("job_title", "Target Role"),
            "strongly_demonstrated": strongly,
            "under_evidenced": [],
            "not_evidenced": not_ev,
            "critical_gaps": [item["skill"] for item in not_ev[:3]],
            "summary": "Deterministic gap analysis compiled from extracted skill matrices."
        }
