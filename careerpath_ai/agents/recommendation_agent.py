"""
Agent 4: Career Recommendation & Roadmap Agent
Generates an actionable, personalized, weekly learning roadmap
directly targeted at the candidate's actual identified skill gaps.
"""

import time
import json
from typing import Dict, Any, List
from core.ollama_client import OllamaClient
from core.prompts import ROADMAP_PROMPT


class RecommendationAgent:
    """Specialized Agent 4: Generates role-specific, gap-driven learning roadmaps."""

    def __init__(self, ollama_client: OllamaClient = None):
        self.name = "Career Recommendation & Roadmap Agent"
        self.ollama = ollama_client or OllamaClient()
        self.system_prompt = ROADMAP_PROMPT

    def generate_roadmap(self, resume_analysis: Dict[str, Any], skill_gap: Dict[str, Any], match_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored 3-phase roadmap targeting specific missing and under-evidenced skills."""
        start_time = time.time()
        job_title = skill_gap.get("job_title") or match_result.get("job_title", "Target Role")
        critical_gaps = skill_gap.get("critical_gaps", [])
        not_evidenced = [i.get("skill") for i in skill_gap.get("not_evidenced", []) if isinstance(i, dict)]
        under_evidenced = [i.get("skill") for i in skill_gap.get("under_evidenced", []) if isinstance(i, dict)]

        user_prompt = f"""Formulate a personalized learning roadmap.
Target Role: {job_title}
Match Score: {match_result.get('overall_score')}%

CRITICAL GAPS TO TARGET:
{json.dumps(critical_gaps)}

MISSING SKILLS (NOT EVIDENCED):
{json.dumps(not_evidenced)}

UNDER-EVIDENCED SKILLS:
{json.dumps(under_evidenced)}

EXISTING STRONG SKILLS (DO NOT RE-TEACH FROM SCRATCH):
{json.dumps([s.get('skill') for s in skill_gap.get('strongly_demonstrated', []) if isinstance(s, dict)])}

Generate a comprehensive roadmap structured into Beginner (Weeks 1-4), Intermediate (Weeks 5-8), and Advanced (Weeks 9-12).
Include weekly objectives, practical tasks, free resource URLs, interview topics, and portfolio suggestions.
Return ONLY valid JSON.
"""
        llm_data = {}
        try:
            llm_data = self.ollama.invoke_json(self.system_prompt, user_prompt)
        except Exception:
            llm_data = self._deterministic_roadmap(job_title, not_evidenced, critical_gaps)

        final_roadmap = self._normalize_roadmap(llm_data, job_title, not_evidenced)
        final_roadmap["_execution_time"] = round(time.time() - start_time, 2)
        final_roadmap["_agent"] = self.name
        return final_roadmap

    def _normalize_roadmap(self, data: Dict[str, Any], job_title: str, missing_skills: List[str]) -> Dict[str, Any]:
        """Ensure consistent schema structure across beginner, intermediate, and advanced levels."""
        res = {
            "job_title": data.get("job_title", job_title),
            "total_duration": data.get("total_duration", "12-16 Weeks"),
            "overview": data.get("overview") or f"Personalized pathway designed to bridge specific skill gaps for the {job_title} role.",
            "beginner": data.get("beginner") if isinstance(data.get("beginner"), dict) else {},
            "intermediate": data.get("intermediate") if isinstance(data.get("intermediate"), dict) else {},
            "advanced": data.get("advanced") if isinstance(data.get("advanced"), dict) else {},
            "interview_topics": data.get("interview_topics", []),
            "portfolio_suggestions": data.get("portfolio_suggestions", []),
            "free_resources": data.get("free_resources", []),
            "summary": data.get("summary") or f"Structured transformation curriculum focused on mastering {', '.join(missing_skills[:3])}."
        }

        # Validate sub-levels
        for key, name in [("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")]:
            lvl = res[key]
            lvl.setdefault("level", name)
            lvl.setdefault("duration", "4 Weeks")
            lvl.setdefault("description", f"{name} phase targeting foundational proficiency.")
            lvl.setdefault("milestones", [])
            lvl.setdefault("projects", [f"{name} Capstone Project for {job_title}"])
            lvl.setdefault("tools", missing_skills[:3])

        if not res["interview_topics"]:
            res["interview_topics"] = [
                f"Core architectural principles in {job_title}",
                "Concurrency, performance tuning, and database optimization",
                "Real-world incident troubleshooting and debugging"
            ]

        if not res["free_resources"]:
            res["free_resources"] = [
                "https://roadmap.sh",
                "https://freecodecamp.org",
                "https://developer.mozilla.org"
            ]

        return res

    def _deterministic_roadmap(self, job_title: str, missing: List[str], critical: List[str]) -> Dict[str, Any]:
        """Deterministic roadmap fallback logic."""
        primary_targets = critical or missing or ["Modern Engineering Standards"]
        p1 = primary_targets[0] if len(primary_targets) > 0 else "Foundations"
        p2 = primary_targets[1] if len(primary_targets) > 1 else "Integration"
        p3 = primary_targets[2] if len(primary_targets) > 2 else "Scalability"

        return {
            "job_title": job_title,
            "total_duration": "12-16 Weeks",
            "overview": f"Targeted roadmap designed to bridge competency gaps for the {job_title} role.",
            "beginner": {
                "level": "Beginner",
                "duration": "Weeks 1-4",
                "description": f"Mastering core fundamentals of {p1} and environment configuration.",
                "milestones": [
                    {
                        "week": "Weeks 1-2",
                        "objective": f"Study syntax, architecture, and design patterns of {p1}",
                        "topics": [f"{p1} Core Concepts", "Development Setup", "Unit Testing"],
                        "practical_tasks": [f"Implement small standalone scripts demonstrating {p1} features"],
                        "resources": ["https://roadmap.sh", "https://docs.python.org/3/"]
                    },
                    {
                        "week": "Weeks 3-4",
                        "objective": f"Integrate {p1} with backend storage and APIs",
                        "topics": ["Data persistence", "Error handling", "API endpoints"],
                        "practical_tasks": ["Build basic CRUD service with automated tests"],
                        "resources": ["https://freecodecamp.org"]
                    }
                ],
                "projects": [f"Foundational {p1} Starter Project"],
                "tools": [p1, "Git"]
            },
            "intermediate": {
                "level": "Intermediate",
                "duration": "Weeks 5-8",
                "description": f"Architecting workflows using {p2} and continuous integration.",
                "milestones": [
                    {
                        "week": "Weeks 5-6",
                        "objective": f"Incorporate {p2} into scalable microservices",
                        "topics": [f"{p2} Pipeline Architecture", "Containerization", "CI/CD"],
                        "practical_tasks": ["Write automated GitHub Actions test and lint pipelines"],
                        "resources": ["https://docs.github.com/actions"]
                    },
                    {
                        "week": "Weeks 7-8",
                        "objective": "Optimize throughput, concurrency, and caching",
                        "topics": ["Redis caching", "Async processing", "Benchmarking"],
                        "practical_tasks": ["Simulate load testing and profile query latencies"],
                        "resources": ["https://redis.io/docs/"]
                    }
                ],
                "projects": [f"Scalable {p2} Production Microservice"],
                "tools": [p2, "Docker"]
            },
            "advanced": {
                "level": "Advanced",
                "duration": "Weeks 9-12+",
                "description": f"Production-grade distributed system design utilizing {p3}.",
                "milestones": [
                    {
                        "week": "Weeks 9-10",
                        "objective": f"Production monitoring, reliability, and security with {p3}",
                        "topics": ["Observability & Metrics", "Vulnerability scans", "Zero-downtime deployment"],
                        "practical_tasks": ["Instrument endpoints with Prometheus and Grafana metrics"],
                        "resources": ["https://prometheus.io"]
                    },
                    {
                        "week": "Weeks 11-12",
                        "objective": f"Capstone portfolio development for {job_title}",
                        "topics": ["End-to-end architecture", "Technical documentation", "System design interview prep"],
                        "practical_tasks": ["Publish polished GitHub repository with comprehensive README & live demo"],
                        "resources": ["https://github.com"]
                    }
                ],
                "projects": [f"Full-Scale {job_title} Capstone Architecture"],
                "tools": [p3, "Kubernetes", "Prometheus"]
            },
            "interview_topics": [
                f"How does {p1} handle high concurrency under production load?",
                f"Explain state management and data consistency in {job_title} architectures.",
                "Describe a situation where you had to debug an intermittent race condition or performance bottleneck."
            ],
            "portfolio_suggestions": [
                f"Publish a production-grade open-source repository showcasing {p1} and {p2}",
                "Document architectural decisions using Architecture Decision Records (ADRs)",
                "Add live interactive demo links and Swagger/OpenAPI documentation"
            ],
            "free_resources": [
                "https://roadmap.sh",
                "https://freecodecamp.org",
                "https://fullstackopen.com",
                "https://github.com/donnemartin/system-design-primer"
            ],
            "summary": f"Comprehensive 12-week roadmap structured specifically to bridge gaps in {', '.join(primary_targets[:3])}."
        }
