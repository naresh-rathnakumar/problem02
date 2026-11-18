"""
Page 4: Career Match Dashboard
Displays transparent weighted match percentages, multi-role ranking,
evidence breakdown, and interactive Plotly visualizations.
"""

import streamlit as st
import pandas as pd
from core.scoring import ScoringEngine


def render_matching_page():
    """Render the career compatibility and ranking dashboard."""
    st.markdown("## 🎯 Career Match Dashboard")
    st.caption("Agent 2 compares your profile with target roles using transparent, explainable scoring criteria.")

    match_results = st.session_state.get("match_results", [])
    if not match_results:
        st.warning("⚠️ No match results available yet. Run the analysis pipeline first.")
        if st.button("⬅️ Configure Job Descriptions"):
            st.session_state.current_page = "Job Descriptions"
            st.rerun()
        return

    # Scoring Methodology Display
    scoring = ScoringEngine()
    with st.expander("📐 Transparent Scoring Formula & Weights", expanded=False):
        st.markdown(scoring.get_methodology_description())

    # 1. Multi-Role Rankings & Bar Chart
    st.markdown("### 🏆 Role Compatibility Rankings")
    top_role = match_results[0]
    st.success(f"🥇 **Best Fit Role:** {top_role.get('job_title')} with **{top_role.get('overall_score', 0):.1f}%** Overall Compatibility")

    # Plotly or Fallback Horizontal Bar Chart
    titles = [m.get("job_title", "Role") for m in match_results]
    scores = [m.get("overall_score", 0.0) for m in match_results]

    try:
        import plotly.express as px
        df_plot = pd.DataFrame({"Job Role": titles, "Match Score (%)": scores})
        df_plot = df_plot.sort_values("Match Score (%)", ascending=True)

        fig_bar = px.bar(
            df_plot,
            x="Match Score (%)",
            y="Job Role",
            orientation="h",
            text="Match Score (%)",
            color="Match Score (%)",
            color_continuous_scale=["#E53E3E", "#DD6B20", "#38A169"],
            range_color=[0, 100],
            title="Overall Role Compatibility Comparison"
        )
        fig_bar.update_layout(
            height=max(260, len(titles) * 55),
            xaxis=dict(range=[0, 100]),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception:
        # Streamlit native chart fallback
        df_bar = pd.DataFrame({"Match Score": scores}, index=titles)
        st.bar_chart(df_bar)

    st.markdown("---")

    # 2. Radar Chart for Skill Dimension Breakdown
    st.markdown("### 📊 Multi-Dimensional Skill Coverage")
    try:
        import plotly.graph_objects as go
        categories = ["Required Skills", "Preferred Skills", "Project Evidence", "Edu & Exp"]
        fig_radar = go.Figure()

        for m in match_results[:4]:
            vals = [
                m.get("required_skills_score", 0),
                m.get("preferred_skills_score", 0),
                m.get("project_evidence_score", 0),
                m.get("education_experience_score", 0)
            ]
            vals.append(vals[0])  # Close radar loop
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=categories + [categories[0]],
                name=m.get("job_title"),
                fill="toself",
                opacity=0.35
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=420,
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    except Exception:
        st.caption("Radar chart visualization renders with Plotly.")

    st.markdown("---")

    # 3. Detailed Per-Role Match Cards
    st.markdown("### 📋 Role-by-Role Factor Breakdown")

    for i, m in enumerate(match_results):
        score = m.get("overall_score", 0.0)
        color_tag = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"

        with st.expander(f"{color_tag} #{i+1} — **{m.get('job_title')}** : **{score:.1f}% Match**", expanded=(i == 0)):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Required Skills (50%)", f"{m.get('required_skills_score', 0):.0f}%")
            c2.metric("Preferred Skills (20%)", f"{m.get('preferred_skills_score', 0):.0f}%")
            c3.metric("Project Evidence (20%)", f"{m.get('project_evidence_score', 0):.0f}%")
            c4.metric("Education & Exp (10%)", f"{m.get('education_experience_score', 0):.0f}%")

            if m.get("suitability"):
                st.info(f"**Objective Suitability Assessment:** {m['suitability']}")

            col_m, col_g = st.columns(2)
            with col_m:
                st.markdown("**✅ Matched Skills & Resume Evidence:**")
                matched = [s for s in m.get("matched_skills", []) if s.get("matched")]
                if matched:
                    for s in matched:
                        badge = "🔴 Required" if s.get("is_required") else "🔵 Preferred"
                        st.markdown(f"• **{s.get('skill')}** ({badge}) — _{s.get('evidence')}_")
                else:
                    st.caption("No matching skills directly verified.")

            with col_g:
                st.markdown("**❌ Missing Skills (Not Evidenced):**")
                missing = m.get("missing_skills", [])
                if missing:
                    for s in missing:
                        st.markdown(f"• `{s}`")
                else:
                    st.caption("All requirements verified in profile.")

    # Navigation
    st.markdown("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Back to Job Descriptions", use_container_width=True):
            st.session_state.current_page = "Job Descriptions"
            st.rerun()
    with col_n:
        if st.button("📊 View Skill Gap Analysis ➡️", type="primary", use_container_width=True):
            st.session_state.current_page = "Skill Gap"
            st.rerun()
