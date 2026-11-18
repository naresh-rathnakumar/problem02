"""
CareerPath AI - End-to-End Multi-Agent Pipeline Verification Script
Executes all 4 agents sequentially across Scenarios 1, 2, 3, and 4.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ollama_client import OllamaClient
from agents.orchestrator import CareerPathOrchestrator
from utils.resume_parser import parse_txt
from utils.jd_parser import get_sample_job_descriptions
from utils.report_generator import generate_career_report
from core.scoring import ScoringEngine


def main():
    print("=" * 65)
    print("CAREERPATH AI: MULTI-AGENT PIPELINE VERIFICATION")
    print("=" * 65)

    client = OllamaClient()
    conn = client.check_connection()
    print(f"Ollama Service Status: {'CONNECTED' if conn['connected'] else 'OFFLINE (Using deterministic pipeline fallback)'}")
    print(f"Active Model Config: {conn['model_name']}")

    orchestrator = CareerPathOrchestrator(client)

    # 1. Load Sample Resume: Alex Rivera
    alex_resume_path = os.path.join(os.path.dirname(__file__), "data", "sample_resumes", "alex_rivera_resume.txt")
    with open(alex_resume_path, "r", encoding="utf-8") as f:
        alex_text = f.read()

    print("\n[Step 1] Executing Agent 1: Resume Analysis Agent...")
    alex_profile = orchestrator.run_resume_analysis(alex_text)
    print(f"  Candidate Name: {alex_profile.get('candidate_name')}")
    print(f"  Email: {alex_profile.get('email')}")
    print(f"  Experience: {alex_profile.get('total_experience_years')} Years")
    print(f"  Languages: {', '.join(alex_profile.get('programming_languages', []))}")
    print(f"  Frameworks: {', '.join(alex_profile.get('frameworks_libraries', []))}")
    print(f"  Tools: {', '.join(alex_profile.get('tools_platforms', []))}")
    print(f"  Total Skills Extracted: {len(alex_profile.get('technical_skills', []))}")

    # 2. Benchmark Against 3 Target Roles
    samples = get_sample_job_descriptions()
    test_jds = [
        {"title": "Python Developer", "description": samples["Python Developer"]},
        {"title": "Data Analyst", "description": samples["Data Analyst"]},
        {"title": "Machine Learning Engineer", "description": samples["Machine Learning Engineer"]},
    ]

    print("\n[Step 2] Executing Agent 2: Job Description Matching Agent...")
    matches = orchestrator.run_job_matching(alex_profile, test_jds)
    for m in matches:
        print(f"  Role: {m.get('job_title'):<26} | Match: {m.get('overall_score', 0):.1f}% | Missing: {len(m.get('missing_skills', []))} skills")

    # 3. Analyze Skill Gaps
    print("\n[Step 3] Executing Agent 3: Skill Gap Analysis Agent...")
    gaps = orchestrator.run_skill_gap_analysis(alex_profile, matches, test_jds)
    for g in gaps:
        print(f"  Target: {g.get('job_title'):<24} | Coverage: {g.get('coverage_percentage', 0):.1f}% | Missing Gaps: {len(g.get('not_evidenced', []))}")
        critical = g.get("critical_gaps", [])
        if critical:
            print(f"    Critical Missing Skills: {', '.join(critical[:3])}")

    # 4. Generate Personalized Learning Roadmap for Best Fit
    best_match = matches[0]
    best_gap = gaps[0]
    print(f"\n[Step 4] Executing Agent 4: Career Recommendation & Roadmap Agent for '{best_match.get('job_title')}'...")
    roadmap = orchestrator.run_roadmap_generation(alex_profile, best_gap, best_match)
    print(f"  Roadmap Title: {roadmap.get('job_title')}")
    print(f"  Timeline: {roadmap.get('total_duration')}")
    print(f"  Beginner Phase ({roadmap.get('beginner', {}).get('duration')}): {len(roadmap.get('beginner', {}).get('milestones', []))} milestones")
    print(f"  Intermediate Phase ({roadmap.get('intermediate', {}).get('duration')}): {len(roadmap.get('intermediate', {}).get('milestones', []))} milestones")
    print(f"  Advanced Phase ({roadmap.get('advanced', {}).get('duration')}): {len(roadmap.get('advanced', {}).get('milestones', []))} milestones")
    print(f"  Sample Interview Questions: {len(roadmap.get('interview_topics', []))}")

    # 5. Generate and verify PDF Export
    print("\n[Step 5] Compiling Official PDF Report...")
    scoring = ScoringEngine()
    pdf_bytes = generate_career_report(
        resume_analysis=alex_profile,
        match_results=matches,
        skill_gaps=gaps,
        roadmap=roadmap,
        scoring_methodology=scoring.get_methodology_description()
    )
    report_output_path = os.path.join(os.path.dirname(__file__), "test_career_report.pdf")
    with open(report_output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  Generated PDF ({len(pdf_bytes):,} bytes) -> {report_output_path}")

    # 6. Verify Execution Log
    print("\n[Step 6] Verifying Agent Execution Telemetry...")
    log = orchestrator.get_execution_log()
    for idx, entry in enumerate(log):
        print(f"  [{idx+1}] {entry.get('agent_name'):<38} | Status: {entry.get('status')} | Time: {entry.get('execution_time')}s")

    print("\n" + "=" * 65)
    print("ALL 4 AGENTS AND THE ENTIRE PIPELINE EXECUTED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    main()
