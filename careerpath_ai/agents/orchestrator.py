"""
Central Multi-Agent Orchestrator
Coordinates sequential execution of the 4 specialized agents:
Resume Analysis Agent -> Job Matching Agent -> Skill Gap Agent -> Recommendation Agent.
Maintains execution logs and structured state pipeline.
"""

import time
from typing import Dict, Any, List, Optional
from core.ollama_client import OllamaClient
from agents.resume_agent import ResumeAnalysisAgent
from agents.job_matching_agent import JobMatchingAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.recommendation_agent import RecommendationAgent


class CareerPathOrchestrator:
    """Multi-Agent Orchestrator coordinating all 4 specialized career agents."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.ollama = ollama_client or OllamaClient()
        self.resume_agent = ResumeAnalysisAgent(self.ollama)
        self.job_matching_agent = JobMatchingAgent(self.ollama)
        self.skill_gap_agent = SkillGapAgent(self.ollama)
        self.recommendation_agent = RecommendationAgent(self.ollama)
        self.execution_log: List[Dict[str, Any]] = []

    def log(self, agent_name: str, status: str, input_summary: str = "", output_summary: str = "", execution_time: float = 0.0, error: str = ""):
        """Record transparent agent execution event."""
        entry = {
            "agent_name": agent_name,
            "status": status,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "execution_time": execution_time,
            "error": error,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self.execution_log.append(entry)
        return entry

    def run_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Execute Agent 1: Resume Analysis Agent."""
        self.log(self.resume_agent.name, "Running", input_summary=f"Raw text ({len(resume_text)} characters)")
        try:
            result = self.resume_agent.analyze(resume_text)
            skills_count = len(result.get("technical_skills", []))
            self.log(
                self.resume_agent.name, "Completed",
                output_summary=f"Extracted {skills_count} skills, {len(result.get('projects', []))} projects for {result.get('candidate_name')}",
                execution_time=result.get("_execution_time", 0.0)
            )
            return result
        except Exception as e:
            self.log(self.resume_agent.name, "Failed", error=str(e))
            raise

    def run_job_matching(self, resume_analysis: Dict[str, Any], job_descriptions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Execute Agent 2: Job Description Matching Agent."""
        self.log(self.job_matching_agent.name, "Running", input_summary=f"Comparing profile against {len(job_descriptions)} job description(s)")
        try:
            results = self.job_matching_agent.match_multiple(resume_analysis, job_descriptions)
            top = results[0] if results else {}
            total_time = sum(r.get("_execution_time", 0.0) for r in results)
            self.log(
                self.job_matching_agent.name, "Completed",
                output_summary=f"Ranked {len(results)} roles. Top match: {top.get('job_title')} ({top.get('overall_score', 0):.1f}%)",
                execution_time=round(total_time, 2)
            )
            return results
        except Exception as e:
            self.log(self.job_matching_agent.name, "Failed", error=str(e))
            raise

    def run_skill_gap_analysis(self, resume_analysis: Dict[str, Any], match_results: List[Dict[str, Any]], job_descriptions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Execute Agent 3: Skill Gap Analysis Agent."""
        self.log(self.skill_gap_agent.name, "Running", input_summary=f"Analyzing gaps across {len(match_results)} matched role(s)")
        try:
            results = self.skill_gap_agent.analyze_multiple(resume_analysis, match_results, job_descriptions)
            total_gaps = sum(len(r.get("not_evidenced", [])) for r in results)
            total_time = sum(r.get("_execution_time", 0.0) for r in results)
            self.log(
                self.skill_gap_agent.name, "Completed",
                output_summary=f"Categorized {total_gaps} total skill gap items across roles with High/Med/Low priorities",
                execution_time=round(total_time, 2)
            )
            return results
        except Exception as e:
            self.log(self.skill_gap_agent.name, "Failed", error=str(e))
            raise

    def run_roadmap_generation(self, resume_analysis: Dict[str, Any], skill_gap: Dict[str, Any], match_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Agent 4: Career Recommendation & Roadmap Agent."""
        title = skill_gap.get("job_title", "Role")
        self.log(self.recommendation_agent.name, "Running", input_summary=f"Formulating personalized curriculum for {title}")
        try:
            result = self.recommendation_agent.generate_roadmap(resume_analysis, skill_gap, match_result)
            self.log(
                self.recommendation_agent.name, "Completed",
                output_summary=f"Synthesized {result.get('total_duration')} 3-tier roadmap with weekly targets & interview topics",
                execution_time=result.get("_execution_time", 0.0)
            )
            return result
        except Exception as e:
            self.log(self.recommendation_agent.name, "Failed", error=str(e))
            raise

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Return the running agent activity log."""
        return self.execution_log
