"""
Page 7: Final Career Report & PDF Download
Comprehensive summary report with downloadable PDF export and live agent execution telemetry.
"""

import importlib
import streamlit as st
import utils.report_generator as report_gen_module
from core.scoring import ScoringEngine


def render_report_page():
    """Render the executive final career report with PDF export."""
    # Ensure fresh module reload
    importlib.reload(report_gen_module)
    generate_career_report = report_gen_module.generate_career_report

    st.markdown("## 📋 Final Career Guidance Report")
    st.caption("Complete resume-to-career analysis with skill gaps, role matches, transparent scoring, and actionable roadmap.")

    resume_analysis = st.session_state.get("resume_analysis")
    match_results = st.session_state.get("match_results", [])
    skill_gaps = st.session_state.get("skill_gaps", [])
    roadmap = st.session_state.get("roadmap", {})
    execution_log = st.session_state.get("execution_log", [])

    if not resume_analysis:
        st.warning("⚠️ No completed analysis data found. Run the analysis first.")
        return

    # PDF Download Button at the top
    st.markdown("### 📥 Export Executive Report")
    try:
        scoring = ScoringEngine()
        pdf_bytes = generate_career_report(
            resume_analysis=resume_analysis,
            match_results=match_results,
            skill_gaps=skill_gaps,
            roadmap=roadmap,
            scoring_methodology=scoring.get_methodology_description()
        )
        
        # Verify valid PDF header
        if not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("Generated stream missing PDF header.")

        raw_cand_name = resume_analysis.get("candidate_name", "Candidate")
        clean_name = "".join(c for c in raw_cand_name if c.isalnum() or c in ("_", "-")).strip() or "Candidate"
        
        st.download_button(
            label="📥 Download Complete Report as PDF",
            data=pdf_bytes,
            file_name=f"CareerPath_AI_Report_{clean_name}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF compilation error: {e}")

    st.markdown("---")

    # 1. Candidate Summary
    st.markdown("### 1. Candidate Profile Summary")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Name:** {resume_analysis.get('candidate_name')}")
    c2.markdown(f"**Email:** {resume_analysis.get('email') or 'Not specified'}")
    c3.markdown(f"**Experience:** {resume_analysis.get('total_experience_years', 0)} Years")

    if resume_analysis.get("summary"):
        st.info(resume_analysis["summary"])

    # 2. Match Scores Summary
    st.markdown("### 2. Multi-Role Compatibility Rankings")
    for m in match_results:
        sc = m.get("overall_score", 0.0)
        st.markdown(f"- **{m.get('job_title')}**: **{sc:.1f}% Match** (Req: {m.get('required_skills_score', 0):.0f}%, Pref: {m.get('preferred_skills_score', 0):.0f}%, Projects: {m.get('project_evidence_score', 0):.0f}%, Edu: {m.get('education_experience_score', 0):.0f}%)")
        st.progress(min(sc / 100.0, 1.0))

    # 3. Target Roadmap Summary
    st.markdown("### 3. Target Career Roadmap")
    if roadmap:
        st.markdown(f"**Target Role:** {roadmap.get('job_title')}")
        st.markdown(f"**Timeline:** {roadmap.get('total_duration')}")
        if roadmap.get("overview"):
            st.caption(roadmap["overview"])

    st.markdown("---")

    # 4. Multi-Agent System Execution Telemetry
    st.markdown("### 🤖 Transparent Agent Execution Telemetry")
    st.caption("Verifiable execution audit log demonstrating each agent's execution status, timing, and structured outputs.")

    if execution_log:
        for idx, entry in enumerate(execution_log):
            status = entry.get("status", "Completed")
            icon = "🟢" if status == "Completed" else "🟡" if status == "Running" else "🔴"
            with st.container():
                st.markdown(f"{icon} **Step {idx+1}: {entry.get('agent_name')}** — `{status}` ({entry.get('execution_time', 0):.2f}s) @ {entry.get('timestamp')}")
                if entry.get("input_summary"):
                    st.caption(f"**Input:** {entry['input_summary']}")
                if entry.get("output_summary"):
                    st.caption(f"**Output:** {entry['output_summary']}")
                if entry.get("error"):
                    st.error(f"Error: {entry['error']}")
    else:
        st.caption("No log entries registered.")

    st.markdown("---")
    col_p, col_h = st.columns(2)
    with col_p:
        if st.button("⬅️ Back to Roadmap", use_container_width=True):
            st.session_state.current_page = "Roadmap"
            st.rerun()
    with col_h:
        if st.button("🏠 Home Dashboard", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()
