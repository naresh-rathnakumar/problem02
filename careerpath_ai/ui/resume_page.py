"""
Page 2: Resume Upload & Analysis
Upload PDF, DOCX, or TXT. View extracted candidate info, skills, education, and edit values.
"""

import streamlit as st
from utils.resume_parser import parse_resume, validate_file


def render_resume_page():
    """Render the resume upload, text extraction, and profile editor view."""
    st.markdown("## 📄 Resume Upload & Profile Extraction")
    st.caption("Upload your resume in PDF, DOCX, or TXT format for analysis by Agent 1.")

    uploaded_file = st.file_uploader(
        "Choose your resume file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        help="Upload standard resume documents up to 10MB."
    )

    if uploaded_file:
        valid, msg = validate_file(uploaded_file)
        if not valid:
            st.error(f"❌ {msg}")
            return

        try:
            raw_text = parse_resume(uploaded_file)
            st.session_state.resume_text = raw_text
            st.success(f"✅ Successfully parsed '{uploaded_file.name}' ({len(raw_text):,} characters extracted)")
        except Exception as e:
            st.error(f"❌ Parsing failed: {str(e)}")
            return

    # If text is available, allow viewing and fast extraction
    if st.session_state.get("resume_text"):
        with st.expander("📝 Extracted Resume Raw Text", expanded=False):
            st.text_area("Plain Text Content", st.session_state.resume_text, height=220, disabled=True)

        # Trigger or show Agent 1 extraction
        if st.session_state.get("resume_analysis") is None:
            if st.button("🔬 Analyze Resume with Agent 1", type="primary"):
                from agents.orchestrator import CareerPathOrchestrator
                from core.ollama_client import OllamaClient
                orchestrator = CareerPathOrchestrator(OllamaClient())
                with st.spinner("Agent 1 is extracting structured qualifications..."):
                    try:
                        res = orchestrator.run_resume_analysis(st.session_state.resume_text)
                        st.session_state.resume_analysis = res
                        st.session_state.execution_log = orchestrator.get_execution_log()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Agent 1 error: {e}")

    # Display Extracted Candidate Profile
    if st.session_state.get("resume_analysis"):
        analysis = st.session_state.resume_analysis

        st.markdown("---")
        st.markdown("### 👤 Extracted Candidate Profile")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Name:** {analysis.get('candidate_name', 'Not specified')}")
            st.markdown(f"**Email:** {analysis.get('email', 'Not specified')}")
        with col2:
            st.markdown(f"**Phone:** {analysis.get('phone', 'Not specified')}")
            st.markdown(f"**Location:** {analysis.get('location', 'Not specified')}")
        with col3:
            st.markdown(f"**Experience:** {analysis.get('total_experience_years', 0.0)} Years")

        if analysis.get("summary"):
            st.info(f"**Professional Summary:** {analysis['summary']}")

        st.markdown("---")

        # Skills Columns
        col_t, col_s = st.columns(2)

        with col_t:
            st.markdown("#### 💻 Technical Skills & Frameworks")
            langs = analysis.get("programming_languages", [])
            fws = analysis.get("frameworks_libraries", [])
            tools = analysis.get("tools_platforms", [])
            dbs = analysis.get("databases", [])

            if langs:
                st.markdown(f"**Languages:** " + " ".join(f"`{l}`" for l in langs))
            if fws:
                st.markdown(f"**Frameworks:** " + " ".join(f"`{f}`" for f in fws))
            if tools:
                st.markdown(f"**Tools & DevOps:** " + " ".join(f"`{t}`" for t in tools))
            if dbs:
                st.markdown(f"**Databases:** " + " ".join(f"`{d}`" for d in dbs))

            st.markdown("**Evidence Classification:**")
            tech_skills = analysis.get("technical_skills", [])
            for ts in tech_skills[:12]:
                if isinstance(ts, dict):
                    ev = ts.get("evidence", "Mentioned")
                    icon = "🟢" if "Strongly" in ev else "🟡"
                    st.markdown(f"{icon} **{ts.get('name')}** — _{ev}_ ({ts.get('context', '')})")

        with col_s:
            st.markdown("#### 🤝 Soft Skills")
            soft_skills = analysis.get("soft_skills", [])
            if soft_skills:
                for ss in soft_skills:
                    if isinstance(ss, dict):
                        st.markdown(f"• **{ss.get('name')}** — _{ss.get('evidence', '')}_")
                    else:
                        st.markdown(f"• {ss}")
            else:
                st.caption("No soft skills explicitly evidenced.")

            st.markdown("#### 🎓 Education")
            for edu in analysis.get("education", []):
                if isinstance(edu, dict):
                    st.markdown(f"• **{edu.get('degree')}** in {edu.get('field', '')} — {edu.get('institution', '')} ({edu.get('year', '')})")

            st.markdown("#### 💼 Experience & Projects")
            for exp in analysis.get("experience", []):
                if isinstance(exp, dict):
                    st.markdown(f"• **{exp.get('title')}** at {exp.get('company')} ({exp.get('duration')})")
            for proj in analysis.get("projects", []):
                if isinstance(proj, dict):
                    st.markdown(f"• **{proj.get('name')}**: {proj.get('description', '')[:90]}...")

        # Interactive Profile Correction Editor
        st.markdown("---")
        with st.expander("✏️ Correct / Edit Extracted Information Before Analysis", expanded=False):
            st.info("You can amend any extracted fields before running job matching.")
            c_name = st.text_input("Candidate Name", value=analysis.get("candidate_name", ""))
            c_email = st.text_input("Candidate Email", value=analysis.get("email", ""))
            c_exp = st.number_input("Experience (Years)", value=float(analysis.get("total_experience_years", 0.0)), step=0.5)

            current_langs = ", ".join(analysis.get("programming_languages", []))
            edit_langs = st.text_input("Programming Languages (comma-separated)", value=current_langs)

            current_fws = ", ".join(analysis.get("frameworks_libraries", []))
            edit_fws = st.text_input("Frameworks & Libraries (comma-separated)", value=current_fws)

            if st.button("💾 Save Profile Corrections"):
                st.session_state.resume_analysis["candidate_name"] = c_name
                st.session_state.resume_analysis["email"] = c_email
                st.session_state.resume_analysis["total_experience_years"] = c_exp
                st.session_state.resume_analysis["programming_languages"] = [x.strip() for x in edit_langs.split(",") if x.strip()]
                st.session_state.resume_analysis["frameworks_libraries"] = [x.strip() for x in edit_fws.split(",") if x.strip()]
                st.success("✅ Profile corrections saved successfully!")
                st.rerun()

        # Step navigation
        st.markdown("---")
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⬅️ Home Dashboard", use_container_width=True):
                st.session_state.current_page = "Home"
                st.rerun()
        with col_next:
            if st.button("💼 Proceed to Job Descriptions ➡️", type="primary", use_container_width=True):
                st.session_state.current_page = "Job Descriptions"
                st.rerun()
