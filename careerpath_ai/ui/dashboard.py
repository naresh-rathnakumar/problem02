"""
Page 1: Home / Dashboard
Overview, system architecture, how it works, and local Ollama live diagnostic panel.
"""

import streamlit as st
import os
from core.ollama_client import OllamaClient


def render_dashboard():
    """Render the main landing page & health diagnostics."""
    # Hero Title & Subtitle
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1B2A4A 0%, #2A4365 100%); padding: 2.5rem 2rem; border-radius: 12px; margin-bottom: 2rem; color: white;">
        <h1 style="color: #FFFFFF; margin: 0; font-size: 2.4rem; font-weight: 700;">
            CareerPath AI
        </h1>
        <p style="color: #CBD5E0; font-size: 1.15rem; margin-top: 0.5rem; margin-bottom: 0;">
            AI-Powered Career Companion & Transparent Skill Gap Analyzer
        </p>
        <p style="color: #A0AEC0; font-size: 0.95rem; margin-top: 0.5rem; max-width: 800px;">
            A multi-agent system running 100% locally on Ollama. Upload your resume, match against job descriptions, diagnose exact skill gaps, and generate personalized learning roadmaps.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Live Ollama Connection Status Card
    st.markdown("### 🔌 Local Ollama Runtime Status")
    client = OllamaClient()
    conn = client.check_connection()

    col1, col2, col3 = st.columns(3)
    with col1:
        if conn["connected"]:
            st.success("🟢 Local Ollama Service: **CONNECTED**")
        else:
            st.error("🔴 Local Ollama Service: **OFFLINE**")

    with col2:
        if conn["model_available"]:
            st.success(f"🟢 Active Model: **{conn['model_name']}**")
        else:
            st.warning(f"🟡 Configured Model: **{conn['model_name']}** (Not yet pulled)")

    with col3:
        st.info(f"🌐 Endpoint: `{conn['base_url']}`")

    if not conn["connected"] or not conn["model_available"]:
        with st.expander("🛠️ Local Ollama Setup & Troubleshooting Instructions", expanded=True):
            st.markdown(client.get_setup_instructions())
            if conn["error"]:
                st.code(f"Diagnostic Error: {conn['error']}")

    st.markdown("---")

    # Workflow Steps
    st.markdown("### 🧭 How CareerPath AI Operates")
    colA, colB, colC, colD = st.columns(4)

    with colA:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 10px; padding: 1.2rem; min-height: 190px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📄</div>
            <strong style="color: #38BDF8; font-size: 1.05rem;">1. Resume Parsing</strong>
            <p style="color: #CBD5E0; font-size: 0.85rem; margin-top: 0.5rem;">
                Agent 1 extracts technical and soft skills with strict evidence verification from PDF, DOCX, or TXT.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 10px; padding: 1.2rem; min-height: 190px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🎯</div>
            <strong style="color: #38BDF8; font-size: 1.05rem;">2. Role Matching</strong>
            <p style="color: #CBD5E0; font-size: 0.85rem; margin-top: 0.5rem;">
                Agent 2 benchmarks your profile against multiple JDs using a transparent, weighted 4-factor scoring engine.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 10px; padding: 1.2rem; min-height: 190px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📊</div>
            <strong style="color: #38BDF8; font-size: 1.05rem;">3. Skill Gap Diagnosis</strong>
            <p style="color: #CBD5E0; font-size: 0.85rem; margin-top: 0.5rem;">
                Agent 3 classifies gaps into Strongly Demonstrated, Under-evidenced, and Not Evidenced with priority tags.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with colD:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 10px; padding: 1.2rem; min-height: 190px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🗺️</div>
            <strong style="color: #38BDF8; font-size: 1.05rem;">4. Custom Roadmap</strong>
            <p style="color: #CBD5E0; font-size: 0.85rem; margin-top: 0.5rem;">
                Agent 4 synthesizes a 3-tier, 12-week roadmap with weekly targets, curated resources, and interview topics.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Multi-Agent Architecture
    st.markdown("### 🤖 Specialized AI Agents")
    st.caption("Each agent operates with its own system prompt, distinct responsibilities, and structured schemas.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **🔬 Agent 1: Resume Analysis Agent**
        - Extracts factual skills, languages, frameworks, education, experience, and projects.
        - Labels evidence level: *Strongly Demonstrated* vs. *Mentioned without sufficient evidence*.
        """)
        st.markdown("""
        **🎯 Agent 2: Job Description Matching Agent**
        - Compares profile against single or multiple job descriptions.
        - Calculates explainable match percentage: Required (50%), Preferred (20%), Projects (20%), Education/Exp (10%).
        """)

    with c2:
        st.markdown("""
        **📊 Agent 3: Skill Gap Analysis Agent**
        - Differentiates confirmed skills from unevidenced competencies.
        - Strict terminology: Labels missing skills as *"Not evidenced in resume"*, never as personal lack.
        """)
        st.markdown("""
        **🗺️ Agent 4: Career Recommendation & Roadmap Agent**
        - Builds dynamic Beginner, Intermediate, and Advanced weekly milestones based on real gaps.
        - Provides project improvements, portfolio suggestions, and interview question banks.
        """)

    st.markdown("---")

    # Call to action
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if st.button("🚀 Start Career Analysis", type="primary", use_container_width=True):
            st.session_state.current_page = "Resume Upload"
            st.rerun()
