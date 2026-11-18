"""
Page 3: Job Description Input & Benchmark Selection
Add one or multiple target job descriptions via quick benchmark selector,
direct paste, or file upload.
"""

import streamlit as st
from utils.jd_parser import get_sample_job_descriptions, parse_jd_file


def render_job_page():
    """Render the job description management view."""
    st.markdown("## 💼 Job Description Selection & Management")
    st.caption("Add one or multiple target job descriptions to benchmark your skills against.")

    if "job_descriptions" not in st.session_state:
        st.session_state.job_descriptions = []

    # 1. Quick Add Official Benchmark Roles
    st.markdown("### 📋 Quick Add: Benchmark Roles")
    samples = get_sample_job_descriptions()
    role_names = list(samples.keys())

    cols = st.columns(4)
    for idx, role in enumerate(role_names):
        with cols[idx % 4]:
            if st.button(f"➕ {role}", key=f"quick_{idx}", use_container_width=True):
                existing_titles = [j.get("title") for j in st.session_state.job_descriptions]
                if role not in existing_titles:
                    st.session_state.job_descriptions.append({
                        "title": role,
                        "description": samples[role]
                    })
                    st.success(f"Added '{role}'")
                    st.rerun()
                else:
                    st.warning(f"'{role}' already added")

    st.markdown("---")

    # 2. Add Custom Job Description
    st.markdown("### ✍️ Add Custom Job Description")
    tab_paste, tab_file = st.tabs(["📝 Paste Description Text", "📁 Upload JD File (.txt, .pdf)"])

    with tab_paste:
        custom_title = st.text_input("Target Role / Job Title", placeholder="e.g. Senior Backend Engineer")
        custom_text = st.text_area("Job Description Content", height=180, placeholder="Paste the job requirements, responsibilities, and qualifications...")
        if st.button("➕ Add Pasted Job Description"):
            if custom_text.strip():
                st.session_state.job_descriptions.append({
                    "title": custom_title.strip() or "Target Role",
                    "description": custom_text.strip()
                })
                st.success("Custom role added!")
                st.rerun()
            else:
                st.warning("Please provide job description text.")

    with tab_file:
        jd_file = st.file_uploader("Upload Job Description (.pdf, .txt)", type=["pdf", "txt"], key="jd_file_upl")
        jd_f_title = st.text_input("Role Title for File", placeholder="e.g. Staff Data Engineer")
        if jd_file and st.button("➕ Add From Uploaded File"):
            try:
                extracted_jd = parse_jd_file(jd_file)
                st.session_state.job_descriptions.append({
                    "title": jd_f_title.strip() or jd_file.name.replace(".pdf", "").replace(".txt", ""),
                    "description": extracted_jd
                })
                st.success(f"Added job description from {jd_file.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing file: {e}")

    st.markdown("---")

    # 3. Currently Configured Target Roles
    st.markdown("### 📑 Configured Job Roles for Comparison")
    if not st.session_state.job_descriptions:
        st.info("No job descriptions added yet. Click one of the benchmark roles above or paste your own.")
    else:
        for i, jd in enumerate(st.session_state.job_descriptions):
            with st.expander(f"Role #{i+1}: **{jd.get('title')}**", expanded=(i == 0)):
                st.text_area(f"Description ({jd.get('title')})", jd.get("description"), height=140, disabled=True, key=f"jd_disp_{i}")
                if st.button(f"🗑️ Remove Role", key=f"del_jd_{i}"):
                    st.session_state.job_descriptions.pop(i)
                    st.rerun()

        st.info(f"**Total Roles for Multi-Role Benchmarking:** {len(st.session_state.job_descriptions)}")

    # Navigation & Pipeline Execution
    st.markdown("---")
    col_back, col_run = st.columns(2)
    with col_back:
        if st.button("⬅️ Back to Resume Upload", use_container_width=True):
            st.session_state.current_page = "Resume Upload"
            st.rerun()

    with col_run:
        can_run = bool(st.session_state.get("resume_text") and st.session_state.job_descriptions)
        if st.button("🚀 Run Full Multi-Agent Pipeline ➡️", type="primary", disabled=not can_run, use_container_width=True):
            st.session_state.run_full_pipeline_trigger = True
            st.session_state.current_page = "Career Match"
            st.rerun()
