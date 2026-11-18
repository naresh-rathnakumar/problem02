"""
CareerPath AI – Your AI-Powered Career Companion
Main Streamlit Application Controller with Multi-Agent Orchestration.
"""

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CareerPath AI – Career Companion",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design Styling (Professional blue, white, and dark navy theme)
st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    .css-1d391kg, div[data-testid="stSidebar"] {
        background-color: #1B2A4A;
        color: white;
    }
    div[data-testid="stSidebar"] h1, 
    div[data-testid="stSidebar"] h2, 
    div[data-testid="stSidebar"] h3, 
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] span {
        color: #E2E8F0 !important;
    }
    /* High-contrast, theme-adaptive cards for all metrics */
    div[data-testid="stMetric"], .stMetric {
        background-color: #1E293B !important;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] span {
        color: #38BDF8 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] > div {
        color: #34D399 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Import View Modules
from ui.dashboard import render_dashboard
from ui.resume_page import render_resume_page
from ui.job_page import render_job_page
from ui.matching_page import render_matching_page
from ui.skill_gap_page import render_skill_gap_page
from ui.roadmap_page import render_roadmap_page
from ui.report_page import render_report_page

# Session State Initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = None
if "job_descriptions" not in st.session_state:
    st.session_state.job_descriptions = []
if "match_results" not in st.session_state:
    st.session_state.match_results = None
if "skill_gaps" not in st.session_state:
    st.session_state.skill_gaps = None
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None
if "execution_log" not in st.session_state:
    st.session_state.execution_log = []


def execute_full_pipeline():
    """Trigger the multi-agent sequential pipeline across all 4 agents."""
    from agents.orchestrator import CareerPathOrchestrator
    from core.ollama_client import OllamaClient

    client = OllamaClient()
    orchestrator = CareerPathOrchestrator(client)

    progress_banner = st.status("🚀 Multi-Agent System Executing...", expanded=True)

    try:
        # Step 1: Agent 1 - Resume Analysis
        progress_banner.write("🔬 Agent 1: Analyzing Resume & extracting skills...")
        if not st.session_state.get("resume_analysis"):
            resume_data = orchestrator.run_resume_analysis(st.session_state.resume_text)
            st.session_state.resume_analysis = resume_data
        else:
            resume_data = st.session_state.resume_analysis

        # Step 2: Agent 2 - Job Description Matching
        progress_banner.write("🎯 Agent 2: Benchmarking against target job roles & computing match scores...")
        matches = orchestrator.run_job_matching(resume_data, st.session_state.job_descriptions)
        st.session_state.match_results = matches

        # Step 3: Agent 3 - Skill Gap Diagnosis
        progress_banner.write("📊 Agent 3: Diagnosing detailed skill gaps & project upgrades...")
        gaps = orchestrator.run_skill_gap_analysis(resume_data, matches, st.session_state.job_descriptions)
        st.session_state.skill_gaps = gaps

        # Step 4: Agent 4 - Learning Roadmap Formulation
        progress_banner.write("🗺️ Agent 4: Formulating 12-week role-specific learning roadmap...")
        best_match = matches[0] if matches else {}
        best_gap = gaps[0] if gaps else {}
        roadmap = orchestrator.run_roadmap_generation(resume_data, best_gap, best_match)
        st.session_state.roadmap = roadmap

        st.session_state.execution_log = orchestrator.get_execution_log()
        progress_banner.update(label="✅ All 4 Agents Completed Analysis Successfully!", state="complete")
        return True

    except Exception as e:
        progress_banner.update(label="❌ Pipeline Failed", state="error")
        st.error(f"Pipeline error: {str(e)}")
        st.session_state.execution_log = orchestrator.get_execution_log()
        return False


# Check for pipeline trigger
if st.session_state.get("run_full_pipeline_trigger"):
    st.session_state.run_full_pipeline_trigger = False
    success = execute_full_pipeline()
    if success:
        st.session_state.current_page = "Career Match"
        st.rerun()


# Sidebar Navigation & Progress Dashboard
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.2rem 0;">
        <h2 style="margin: 0; color: #FFFFFF; font-size: 1.6rem; font-weight: 700;">🎯 CareerPath AI</h2>
        <p style="margin: 0; color: #CBD5E0; font-size: 0.85rem;">Multi-Agent Career Companion</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    nav_pages = [
        ("🏠", "Home"),
        ("📄", "Resume Upload"),
        ("💼", "Job Descriptions"),
        ("🎯", "Career Match"),
        ("📊", "Skill Gap"),
        ("🗺️", "Roadmap"),
        ("📋", "Report"),
    ]

    for icon, page in nav_pages:
        is_active = (st.session_state.current_page == page)
        button_type = "primary" if is_active else "secondary"
        if st.button(f"{icon} {page}", key=f"nav_btn_{page}", use_container_width=True, type=button_type):
            st.session_state.current_page = page
            st.rerun()

    st.markdown("---")

    # Workflow Progress Meter
    st.markdown("### 📈 Analysis Status")
    has_resume = bool(st.session_state.get("resume_text"))
    has_jds = bool(st.session_state.get("job_descriptions"))
    has_match = bool(st.session_state.get("match_results"))
    has_gaps = bool(st.session_state.get("skill_gaps"))
    has_roadmap = bool(st.session_state.get("roadmap"))

    steps = [
        ("Resume Uploaded", has_resume),
        ("Job Descriptions Added", has_jds),
        ("Role Matching Done", has_match),
        ("Skill Gaps Diagnosed", has_gaps),
        ("Roadmap Generated", has_roadmap),
    ]

    for label, done in steps:
        mark = "✅" if done else "⬜"
        st.markdown(f"{mark} {label}")

    pct_done = sum(1 for _, d in steps if d) / len(steps)
    st.progress(pct_done)

    st.markdown("---")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    st.caption(f"🧠 Local Model: `{model_name}`")
    st.caption("🔒 100% Local Inference via Ollama")


# Render Active Page
active_page = st.session_state.current_page
if active_page == "Home":
    render_dashboard()
elif active_page == "Resume Upload":
    render_resume_page()
elif active_page == "Job Descriptions":
    render_job_page()
elif active_page == "Career Match":
    render_matching_page()
elif active_page == "Skill Gap":
    render_skill_gap_page()
elif active_page == "Roadmap":
    render_roadmap_page()
elif active_page == "Report":
    render_report_page()
