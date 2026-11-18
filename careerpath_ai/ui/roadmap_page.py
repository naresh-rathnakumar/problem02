"""
Page 6: Personalized Career Roadmap
Dynamic, gap-driven learning roadmap segmented into Beginner, Intermediate, and Advanced
with weekly milestones, practical projects, curated resources, and interview prep.
"""

import streamlit as st


def render_roadmap_page():
    """Render the personalized career roadmap view."""
    st.markdown("## 🗺️ Personalized Career Roadmap")
    st.caption("Agent 4 synthesizes a customized, gap-driven learning path based strictly on your identified skill gaps.")

    roadmap = st.session_state.get("roadmap")
    match_results = st.session_state.get("match_results", [])
    skill_gaps = st.session_state.get("skill_gaps", [])

    if not roadmap:
        st.warning("⚠️ No roadmap generated yet. Complete the analysis pipeline first.")
        return

    # Role switcher allowing roadmap regeneration for other roles
    if len(match_results) > 1:
        titles = [m.get("job_title") for m in match_results]
        current_title = roadmap.get("job_title")
        cur_idx = titles.index(current_title) if current_title in titles else 0

        selected_role = st.selectbox("Generate Roadmap for Target Role:", titles, index=cur_idx)
        if selected_role != current_title:
            if st.button(f"🔄 Generate Fresh Roadmap for '{selected_role}'", type="secondary"):
                new_idx = titles.index(selected_role)
                from agents.orchestrator import CareerPathOrchestrator
                from core.ollama_client import OllamaClient
                orchestrator = CareerPathOrchestrator(OllamaClient())
                with st.spinner(f"Agent 4 is formulating custom roadmap for {selected_role}..."):
                    new_rm = orchestrator.run_roadmap_generation(
                        st.session_state.resume_analysis,
                        skill_gaps[new_idx],
                        match_results[new_idx]
                    )
                    st.session_state.roadmap = new_rm
                    st.rerun()

    st.markdown(f"### 🎯 Roadmap for: **{roadmap.get('job_title')}**")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Estimated Duration", roadmap.get("total_duration", "12 Weeks"))
    with col2:
        if roadmap.get("overview"):
            st.info(f"**Curriculum Focus:** {roadmap['overview']}")

    st.markdown("---")

    # Beginner Level
    beginner = roadmap.get("beginner", {})
    if isinstance(beginner, dict) and beginner:
        with st.expander(f"🟢 **PHASE 1: BEGINNER** — {beginner.get('duration', 'Weeks 1-4')}", expanded=True):
            if beginner.get("description"):
                st.markdown(f"*{beginner['description']}*")

            milestones = beginner.get("milestones", [])
            for ms in milestones:
                if isinstance(ms, dict):
                    st.markdown(f"#### 📅 {ms.get('week')}: {ms.get('objective')}")
                    if ms.get("topics"):
                        st.markdown("**Core Topics:** " + ", ".join(ms["topics"]))
                    if ms.get("practical_tasks"):
                        for t in ms["practical_tasks"]:
                            st.markdown(f"  • ✅ {t}")
                    if ms.get("resources"):
                        st.markdown("**Free Resources:** " + ", ".join(f"[{r}]({r})" if "http" in r else r for r in ms["resources"]))
                    st.markdown("---")

            if beginner.get("projects"):
                st.markdown(f"**📦 Recommended Beginner Projects:** {', '.join(beginner['projects'])}")
            if beginner.get("tools"):
                st.markdown(f"**🛠️ Primary Tools:** {', '.join(beginner['tools'])}")

    # Intermediate Level
    intermediate = roadmap.get("intermediate", {})
    if isinstance(intermediate, dict) and intermediate:
        with st.expander(f"🟡 **PHASE 2: INTERMEDIATE** — {intermediate.get('duration', 'Weeks 5-8')}", expanded=True):
            if intermediate.get("description"):
                st.markdown(f"*{intermediate['description']}*")

            milestones = intermediate.get("milestones", [])
            for ms in milestones:
                if isinstance(ms, dict):
                    st.markdown(f"#### 📅 {ms.get('week')}: {ms.get('objective')}")
                    if ms.get("topics"):
                        st.markdown("**Core Topics:** " + ", ".join(ms["topics"]))
                    if ms.get("practical_tasks"):
                        for t in ms["practical_tasks"]:
                            st.markdown(f"  • ✅ {t}")
                    if ms.get("resources"):
                        st.markdown("**Free Resources:** " + ", ".join(f"[{r}]({r})" if "http" in r else r for r in ms["resources"]))
                    st.markdown("---")

            if intermediate.get("projects"):
                st.markdown(f"**📦 Recommended Intermediate Projects:** {', '.join(intermediate['projects'])}")
            if intermediate.get("tools"):
                st.markdown(f"**🛠️ Primary Tools:** {', '.join(intermediate['tools'])}")

    # Advanced Level
    advanced = roadmap.get("advanced", {})
    if isinstance(advanced, dict) and advanced:
        with st.expander(f"🔴 **PHASE 3: ADVANCED & PRODUCTION** — {advanced.get('duration', 'Weeks 9-12+')}", expanded=True):
            if advanced.get("description"):
                st.markdown(f"*{advanced['description']}*")

            milestones = advanced.get("milestones", [])
            for ms in milestones:
                if isinstance(ms, dict):
                    st.markdown(f"#### 📅 {ms.get('week')}: {ms.get('objective')}")
                    if ms.get("topics"):
                        st.markdown("**Core Topics:** " + ", ".join(ms["topics"]))
                    if ms.get("practical_tasks"):
                        for t in ms["practical_tasks"]:
                            st.markdown(f"  • ✅ {t}")
                    if ms.get("resources"):
                        st.markdown("**Free Resources:** " + ", ".join(f"[{r}]({r})" if "http" in r else r for r in ms["resources"]))
                    st.markdown("---")

            if advanced.get("projects"):
                st.markdown(f"**📦 Capstone Portfolio Project:** {', '.join(advanced['projects'])}")
            if advanced.get("tools"):
                st.markdown(f"**🛠️ Production Tools:** {', '.join(advanced['tools'])}")

    st.markdown("---")

    # Interview Prep & Portfolio Suggestions
    col_int, col_port = st.columns(2)
    with col_int:
        st.markdown("### 🎤 Role-Specific Interview Questions")
        topics = roadmap.get("interview_topics", [])
        if topics:
            for top in topics:
                st.markdown(f"- ❓ **{top}**")
        else:
            st.caption("No specific interview topics generated.")

    with col_port:
        st.markdown("### 💼 Portfolio Enhancement Milestones")
        suggs = roadmap.get("portfolio_suggestions", [])
        if suggs:
            for s in suggs:
                st.markdown(f"- 🚀 **{s}**")
        else:
            st.caption("No portfolio suggestions generated.")

    # Navigation
    st.markdown("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Back to Skill Gaps", use_container_width=True):
            st.session_state.current_page = "Skill Gap"
            st.rerun()
    with col_n:
        if st.button("📋 View Final Career Report ➡️", type="primary", use_container_width=True):
            st.session_state.current_page = "Report"
            st.rerun()
