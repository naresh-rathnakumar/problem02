"""
Pydantic schemas for structured data exchange between agents.
All agent communication uses these schemas for type safety and validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SkillPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SkillCategory(str, Enum):
    TECHNICAL = "Technical"
    SOFT = "Soft"
    PROGRAMMING_LANGUAGE = "Programming Language"
    FRAMEWORK = "Framework/Library"
    TOOL = "Tool/Platform"
    DATABASE = "Database"
    CLOUD = "Cloud/DevOps"
    OTHER = "Other"


class SkillEvidence(str, Enum):
    STRONGLY_DEMONSTRATED = "Strongly Demonstrated"
    MENTIONED = "Mentioned but Insufficiently Demonstrated"
    NOT_EVIDENCED = "Not Evidenced in Resume"


class ExtractedSkill(BaseModel):
    name: str = Field(description="Skill name")
    category: str = Field(default="Technical", description="Skill category")
    evidence: str = Field(default="Mentioned", description="Evidence level")
    context: str = Field(default="", description="Where this skill appears in the resume")


class Education(BaseModel):
    degree: str = Field(default="", description="Degree name")
    institution: str = Field(default="", description="Institution name")
    year: str = Field(default="", description="Year of completion")
    field: str = Field(default="", description="Field of study")
    gpa: str = Field(default="", description="GPA if mentioned")


class Experience(BaseModel):
    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company name")
    duration: str = Field(default="", description="Duration of employment")
    description: str = Field(default="", description="Key responsibilities")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class Project(BaseModel):
    name: str = Field(default="", description="Project name")
    description: str = Field(default="", description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: str = Field(default="", description="Project URL if available")


class Certification(BaseModel):
    name: str = Field(default="", description="Certification name")
    issuer: str = Field(default="", description="Issuing organization")
    year: str = Field(default="", description="Year obtained")


class ResumeAnalysis(BaseModel):
    """Output schema for Resume Analysis Agent"""
    candidate_name: str = Field(default="Not specified", description="Candidate name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    location: str = Field(default="", description="Location")
    summary: str = Field(default="", description="Professional summary")
    technical_skills: List[ExtractedSkill] = Field(default_factory=list)
    soft_skills: List[ExtractedSkill] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks_libraries: List[str] = Field(default_factory=list)
    tools_platforms: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    total_experience_years: float = Field(default=0.0)
    raw_text: str = Field(default="", description="Original resume text")


class JobRequirement(BaseModel):
    """Parsed job description requirements"""
    title: str = Field(default="", description="Job title")
    company: str = Field(default="", description="Company name")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_experience_years: float = Field(default=0.0)
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    description: str = Field(default="", description="Full job description text")


class SkillMatch(BaseModel):
    skill: str = Field(description="Skill name")
    matched: bool = Field(default=False)
    evidence: str = Field(default="Not Evidenced in Resume")
    is_required: bool = Field(default=True)


class JobMatchResult(BaseModel):
    """Output schema for Job Matching Agent"""
    job_title: str = Field(default="")
    overall_score: float = Field(default=0.0, description="Overall match percentage 0-100")
    required_skills_score: float = Field(default=0.0)
    preferred_skills_score: float = Field(default=0.0)
    project_evidence_score: float = Field(default=0.0)
    education_experience_score: float = Field(default=0.0)
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    matching_reasons: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    suitability: str = Field(default="", description="Why suitable or unsuitable")


class SkillGapItem(BaseModel):
    """Individual skill gap entry"""
    skill: str = Field(description="Skill name")
    category: str = Field(default="Technical")
    current_evidence: str = Field(default="Not Evidenced in Resume")
    job_requirement: str = Field(default="Required")
    priority: str = Field(default="Medium")
    importance_reason: str = Field(default="")
    recommendation: str = Field(default="")
    improvable_projects: List[str] = Field(default_factory=list)


class SkillGapAnalysis(BaseModel):
    """Output schema for Skill Gap Analysis Agent"""
    job_title: str = Field(default="")
    strongly_demonstrated: List[SkillGapItem] = Field(default_factory=list)
    under_evidenced: List[SkillGapItem] = Field(default_factory=list)
    not_evidenced: List[SkillGapItem] = Field(default_factory=list)
    total_required_skills: int = Field(default=0)
    coverage_percentage: float = Field(default=0.0)
    critical_gaps: List[str] = Field(default_factory=list)
    summary: str = Field(default="")


class LearningMilestone(BaseModel):
    week: str = Field(default="")
    objective: str = Field(default="")
    topics: List[str] = Field(default_factory=list)
    practical_tasks: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)


class RoadmapLevel(BaseModel):
    level: str = Field(default="Beginner")
    duration: str = Field(default="")
    description: str = Field(default="")
    milestones: List[LearningMilestone] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CareerRoadmap(BaseModel):
    """Output schema for Career Recommendation Agent"""
    job_title: str = Field(default="")
    total_duration: str = Field(default="")
    overview: str = Field(default="")
    beginner: RoadmapLevel = Field(default_factory=lambda: RoadmapLevel(level="Beginner"))
    intermediate: RoadmapLevel = Field(default_factory=lambda: RoadmapLevel(level="Intermediate"))
    advanced: RoadmapLevel = Field(default_factory=lambda: RoadmapLevel(level="Advanced"))
    interview_topics: List[str] = Field(default_factory=list)
    portfolio_suggestions: List[str] = Field(default_factory=list)
    free_resources: List[str] = Field(default_factory=list)
    summary: str = Field(default="")


class AgentExecutionLog(BaseModel):
    """Log entry for agent execution tracking"""
    agent_name: str
    status: str = Field(default="pending")
    input_summary: str = Field(default="")
    output_summary: str = Field(default="")
    execution_time: float = Field(default=0.0)
    error: str = Field(default="")
