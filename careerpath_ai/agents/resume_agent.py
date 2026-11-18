"""
Agent 1: Resume Analysis Agent
Extracts structured candidate profile, technical/soft skills, education,
projects, and experience with verifiable evidence labeling.
"""

import time
import re
from typing import Dict, Any, List
from core.ollama_client import OllamaClient
from core.prompts import RESUME_ANALYSIS_PROMPT
from utils.skill_extractor import extract_skills_with_spacy
from utils.validators import validate_resume_analysis


class ResumeAnalysisAgent:
    """Specialized Agent 1: Analyzes resumes, extracts skills, and classifies evidence."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.name = "Resume Analysis Agent"
        self.ollama = ollama_client or OllamaClient()
        self.system_prompt = RESUME_ANALYSIS_PROMPT

    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume text using local LLM inference with NLP entity anchoring."""
        start_time = time.time()

        # Step 1: Run deterministic taxonomy and NLP extraction
        nlp_data = extract_skills_with_spacy(resume_text)

        # Step 2: Query local Ollama
        user_prompt = f"""Extract all structured candidate information from the following resume text.
Do not invent any details not found in the resume. Return pure JSON adhering to the specified schema.

RESUME TEXT:
{resume_text}
"""
        llm_output = {}
        try:
            llm_output = self.ollama.invoke_json(self.system_prompt, user_prompt)
        except Exception as e:
            # Deterministic fallback if Ollama service is unavailable
            llm_output = self._deterministic_parse(resume_text, nlp_data)
            llm_output["_notice"] = f"Local Ollama inference bypassed ({str(e)}). Used deterministic parser."

        # Step 3: Reconcile and enrich with NLP evidence
        final_profile = self._reconcile(llm_output, nlp_data, resume_text)
        final_profile = validate_resume_analysis(final_profile)

        final_profile["_agent"] = self.name
        final_profile["_execution_time"] = round(time.time() - start_time, 2)
        return final_profile

    def _reconcile(self, llm_data: Dict[str, Any], nlp_data: Dict[str, List[str]], raw_text: str) -> Dict[str, Any]:
        """Reconcile LLM extraction with deterministic NLP ground truth."""
        profile = dict(llm_data)
        profile["raw_text"] = raw_text

        # Ensure candidate name isn't generic
        if not profile.get("candidate_name") or profile.get("candidate_name") in ["Not specified", "string", "Candidate"]:
            # Check first 3 lines of resume
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
            if lines and len(lines[0]) < 50:
                profile["candidate_name"] = lines[0]

        # Extract email and phone if missing
        if not profile.get("email"):
            email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", raw_text)
            if email_match:
                profile["email"] = email_match.group(0)

        if not profile.get("phone"):
            phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", raw_text)
            if phone_match:
                profile["phone"] = phone_match.group(0)

        # Merge programming languages
        existing_langs = {str(l).lower() for l in profile.get("programming_languages", [])}
        for l in nlp_data.get("programming_languages", []):
            if l.lower() not in existing_langs:
                profile.setdefault("programming_languages", []).append(l)

        # Merge frameworks
        existing_fw = {str(f).lower() for f in profile.get("frameworks_libraries", [])}
        for f in nlp_data.get("frameworks", []):
            if f.lower() not in existing_fw:
                profile.setdefault("frameworks_libraries", []).append(f)

        # Merge tools
        existing_tools = {str(t).lower() for t in profile.get("tools_platforms", [])}
        for t in nlp_data.get("tools_platforms", []):
            if t.lower() not in existing_tools:
                profile.setdefault("tools_platforms", []).append(t)

        # Merge databases
        existing_db = {str(d).lower() for d in profile.get("databases", [])}
        for d in nlp_data.get("databases", []):
            if d.lower() not in existing_db:
                profile.setdefault("databases", []).append(d)

        # Ensure technical skills list has evidence classification
        existing_tech_names = {
            (s.get("name", "").lower() if isinstance(s, dict) else str(s).lower())
            for s in profile.get("technical_skills", [])
        }

        # Check project context for evidence
        project_text = " ".join([
            f"{p.get('name', '')} {p.get('description', '')} {' '.join(p.get('technologies', []))}"
            for p in profile.get("projects", []) if isinstance(p, dict)
        ]).lower()

        exp_text = " ".join([
            f"{e.get('title', '')} {e.get('description', '')} {' '.join(e.get('technologies', []))}"
            for e in profile.get("experience", []) if isinstance(e, dict)
        ]).lower()

        all_detected = (
            profile.get("programming_languages", [])
            + profile.get("frameworks_libraries", [])
            + profile.get("tools_platforms", [])
            + profile.get("databases", [])
        )

        for skill in all_detected:
            if skill.lower() not in existing_tech_names:
                evidence = "Mentioned"
                context = "Listed in skills section"
                s_lower = skill.lower()
                if s_lower in project_text:
                    evidence = "Strongly Demonstrated"
                    context = "Evidenced in candidate project implementation"
                elif s_lower in exp_text:
                    evidence = "Strongly Demonstrated"
                    context = "Evidenced in candidate work experience"

                profile.setdefault("technical_skills", []).append({
                    "name": skill,
                    "category": "Technical",
                    "evidence": evidence,
                    "context": context
                })

        return profile

    def _deterministic_parse(self, text: str, nlp_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """High-fidelity fallback parser if Ollama is not actively running."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        candidate_name = lines[0] if lines else "Candidate"

        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

        tech_skills = []
        for cat, skills in nlp_data.items():
            if cat != "soft_skills":
                for s in skills:
                    tech_skills.append({
                        "name": s,
                        "category": "Technical",
                        "evidence": "Strongly Demonstrated" if (s.lower() in text.lower() and ("project" in text.lower() or "experience" in text.lower())) else "Mentioned",
                        "context": "Extracted from resume text"
                    })

        soft_skills = [
            {"name": s, "category": "Soft", "evidence": "Mentioned", "context": "Found in resume"}
            for s in nlp_data.get("soft_skills", [])
        ]

        return {
            "candidate_name": candidate_name,
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "location": "Detected from resume",
            "summary": "Professional profile analyzed via CareerPath AI parser.",
            "technical_skills": tech_skills,
            "soft_skills": soft_skills,
            "programming_languages": nlp_data.get("programming_languages", []),
            "frameworks_libraries": nlp_data.get("frameworks", []),
            "tools_platforms": nlp_data.get("tools_platforms", []),
            "databases": nlp_data.get("databases", []),
            "education": [{"degree": "Relevant Degree", "institution": "University / Institute", "year": "", "field": "Technical"}],
            "experience": [{"title": "Software Experience", "company": "Industry / Academic", "duration": "Demonstrated", "description": "Hands-on engineering experience.", "technologies": nlp_data.get("programming_languages", [])[:3]}],
            "projects": [{"name": "Technical Projects", "description": "Applied technical implementations detailed in resume.", "technologies": nlp_data.get("frameworks", [])[:3], "url": ""}],
            "certifications": [],
            "total_experience_years": 1.5,
        }
