"""
Page 5: Skill Gap Analysis
Interactive structured table with High, Medium, Low priority indicators,
differentiating Strongly Demonstrated, Under-Evidenced, and Not Evidenced in Resume.
"""

import streamlit as st
import pandas as pd


def render_skill_gap_page():
    """Render the structured skill gap breakdown view."""
    st.markdown("## 📊 Skill Gap Analysis")
    st.caption("Agent 3 diagnoses specific skill discrepancies and categorizes them with priority ratings.")

    skill_gaps = st.session_state.get("skill_gaps", [])
    if not skill_gaps:
        st.warning("⚠️ No skill gap data available. Please run the analysis first.")
        return

    # Role Selector
    role_titles = [g.get("job_title", f"Role #{i+1}") for i, g in enumerate(skill_gaps)]
    selected_role = st.selectbox("Select Target Role to Inspect:", role_titles)
    selected_idx = role_titles.index(selected_role)
    gap = skill_gaps[selected_idx]

    # Metrics Summary
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Analyzed Skills", gap.get("total_required_skills", 0))
    c2.metric("Skill Coverage", f"{gap.get('coverage_percentage', 0.0):.1f}%")
    c3.metric("Strongly Evidenced", len(gap.get("strongly_demonstrated", [])))
    c4.metric("Unevidenced Gaps", len(gap.get("not_evidenced", [])))

    if gap.get("summary"):
        st.info(f"**Executive Gap Summary:** {gap['summary']}")

    # Critical Gaps Alert
    critical = gap.get("critical_gaps", [])
    if critical:
        st.markdown("### 🚨 Critical Dealbreaker Gaps")
        st.error(f"High-Priority Missing Requirements: **{', '.join(critical)}**")

    st.markdown("---")

    # 1. Skills Not Evidenced in Resume (Structured Table)
    st.markdown("### 🔴 Skills Not Evidenced in Resume")
    st.caption("Skills required or preferred for this role that have NO verified evidence in the resume.")

    not_ev = gap.get("not_evidenced", [])
    if not_ev:
        rows = []
        for item in not_ev:
            if isinstance(item, dict):
                prio = item.get("priority", "Medium")
                prio_tag = "🔴 High" if prio == "High" else "🟡 Medium" if prio == "Medium" else "🟢 Low"
                rows.append({
                    "Skill": item.get("skill", ""),
                    "Category": item.get("category", "Technical"),
                    "Current Evidence": item.get("current_evidence", "Not evidenced in resume"),
                    "Job Requirement": item.get("job_requirement", "Required"),
                    "Priority": prio_tag,
                    "Recommendation": item.get("recommendation", "")
                })

        df_not_ev = pd.DataFrame(rows)
        st.dataframe(df_not_ev, use_container_width=True, hide_index=True)

        with st.expander("🔍 Improvable Candidate Projects for Missing Skills", expanded=False):
            for item in not_ev:
                projs = item.get("improvable_projects", [])
                if projs:
                    st.markdown(f"- **{item.get('skill')}**: Could be incorporated into existing project **{', '.join(projs)}**")
    else:
        st.success("🎉 No missing skills detected for this role!")

    st.markdown("---")

    # 2. Under-Evidenced Skills
    st.markdown("### 🟡 Under-Evidenced Skills")
    st.caption("Skills mentioned in the resume or skills section but lacking demonstrable project outcomes or code metrics.")

    under = gap.get("under_evidenced", [])
    if under:
        rows_u = []
        for item in under:
            if isinstance(item, dict):
                rows_u.append({
                    "Skill": item.get("skill", ""),
                    "Category": item.get("category", "Technical"),
                    "Current Evidence": item.get("current_evidence", "Mentioned only"),
                    "Priority": item.get("priority", "Medium"),
                    "Recommendation": item.get("recommendation", "")
                })
        st.dataframe(pd.DataFrame(rows_u), use_container_width=True, hide_index=True)
    else:
        st.caption("No under-evidenced skills flagged.")

    st.markdown("---")

    # 3. Strongly Demonstrated Skills
    st.markdown("### 🟢 Strongly Demonstrated Skills")
    strong = gap.get("strongly_demonstrated", [])
    if strong:
        rows_s = []
        for item in strong:
            if isinstance(item, dict):
                rows_s.append({
                    "Skill": item.get("skill", ""),
                    "Evidence in Resume": item.get("current_evidence", "Evidenced in projects/experience"),
                    "Importance for Role": item.get("importance_reason", "")
                })
        st.dataframe(pd.DataFrame(rows_s), use_container_width=True, hide_index=True)

    # Navigation
    st.markdown("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Back to Match Dashboard", use_container_width=True):
            st.session_state.current_page = "Career Match"
            st.rerun()
    with col_n:
        if st.button("🗺️ View Personalized Learning Roadmap ➡️", type="primary", use_container_width=True):
            st.session_state.selected_roadmap_idx = selected_idx
            st.session_state.current_page = "Roadmap"
            st.rerun()
