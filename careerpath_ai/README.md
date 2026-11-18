# CareerPath AI – AI-Powered Career Companion & Skill Gap Analyzer

**Problem Statement TP02:** Students and junior engineers often struggle to understand which job roles fit their current profile, which skills they lack evidence for, and how to acquire those skills methodically.

**CareerPath AI** is an enterprise-grade multi-agent career guidance system that:
1. **Parses & extracts** technical and soft skills from resumes (PDF, DOCX, TXT) with evidence verification.
2. **Benchmarks & ranks** candidate profiles against one or multiple job descriptions using an explainable, weighted scoring model.
3. **Diagnoses skill gaps** by classifying skills into *Strongly Demonstrated*, *Under-Evidenced*, and *Not Evidenced in Resume* with High/Med/Low priorities.
4. **Synthesizes a personalized 12-week roadmap** segmented into Beginner, Intermediate, and Advanced milestones, complete with project ideas, free resources, and interview preparation questions.
5. **Generates an executive PDF report** with complete analysis telemetry.

---

## 🏛️ Multi-Agent Architecture

CareerPath AI implements an explicit 4-agent sequential workflow:

```
[Uploaded Resume: PDF / DOCX / TXT]
                ↓
    ┌───────────────────────────────────────────────┐
    │  Agent 1: Resume Analysis Agent               │
    │  - Factual extraction (Skills, Edu, Exp, Proj)│
    │  - Evidence level tagging (Proven vs Mentioned│
    └───────────────────────────────────────────────┘
                ↓  [Structured Candidate Profile JSON]
    ┌───────────────────────────────────────────────┐
    │  Agent 2: Job Description Matching Agent      │
    │  - Multi-JD requirement extraction           │
    │  - 4-Factor Weighted Mathematical Scoring     │
    └───────────────────────────────────────────────┘
                ↓  [Role Match Rankings & Matched/Missing Skills]
    ┌───────────────────────────────────────────────┐
    │  Agent 3: Skill Gap Analysis Agent            │
    │  - Categorization (Strong / Under / Missing)  │
    │  - Priority assignment (High, Med, Low)       │
    │  - Project upgrade recommendations            │
    └───────────────────────────────────────────────┘
                ↓  [Actionable Gap Diagnostics JSON]
    ┌───────────────────────────────────────────────┐
    │  Agent 4: Career Recommendation & Roadmap Agent│
    │  - 3-Phase Milestone Roadmap (Beg/Int/Adv)    │
    │  - Weekly tasks, tools, free URLs, interview Qs│
    └───────────────────────────────────────────────┘
                ↓
[Interactive Streamlit Dashboard + Exportable PDF Guidance Report]
```

---

## 🛠️ Technology Stack (Strict Compliance)

- **Language:** Python 3.12+
- **Frontend:** Streamlit (Custom blue, white, dark navy theme)
- **Local LLM Engine:** Ollama (`llama3.1:8b`, configurable via `.env`)
- **LLM Integration:** LangChain (`ChatOllama`) & LangGraph architecture
- **NLP & Parsing:** spaCy, PyMuPDF (`fitz`), `python-docx`, `pypdf`
- **Data & Visualization:** Pandas, Plotly (Bar charts, radar charts)
- **Report Generation:** `fpdf2`

> **LOCAL LLM ONLY:** Cloud APIs (OpenAI, Gemini, Claude, Groq) are prohibited. All inference executes locally on Ollama.

---

## 📐 Transparent Scoring Methodology

The compatibility score is calculated deterministically:

| Factor | Weight | Evaluation Criteria |
|---|---|---|
| **Required Technical Skills** | **50%** | Percentage of core mandatory skills evidenced in resume |
| **Preferred Technical Skills** | **20%** | Percentage of nice-to-have skills evidenced in resume |
| **Project & Work Evidence** | **20%** | Skills corroborated in project descriptions or work history |
| **Education & Experience** | **10%** | Alignment with minimum experience years and degree field |

---

## 🚀 Quickstart Guide (Windows / VS Code)

### 1. Prerequisites: Install & Start Ollama
1. Download Ollama from [https://ollama.com/download/windows](https://ollama.com/download/windows).
2. Open PowerShell and start the Ollama service:
   ```powershell
   ollama serve
   ```
3. In another terminal, pull the default model:
   ```powershell
   ollama pull llama3.1:8b
   ```
4. Verify the model is available:
   ```powershell
   ollama list
   ```

### 2. Setup Python Environment
```powershell
cd c:\Users\HP\Desktop\problem02\careerpath_ai

# Optional: Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```powershell
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Hackathon Demonstration Scenarios

Four pre-built demonstration scenarios are included in `data/sample_resumes/`:

### Scenario 1: Python Developer Benchmark
- Upload `data/sample_resumes/alex_rivera_resume.txt`.
- Select the **Python Developer** benchmark job description.
- **Result:** High match (~75-85%). Missing containerization/CI/CD (Docker, Celery).

### Scenario 2: Cross-Role Comparison (Data Analyst)
- Keep Alex Rivera's resume and add **Data Analyst**.
- **Result:** Demonstrates how the match score shifts based on statistical analysis & BI visualization requirements (Tableau, Power BI).

### Scenario 3: Machine Learning Engineer & Roadmap Differentiation
- Compare against **Machine Learning Engineer**.
- **Result:** Distinct roadmap generated focusing on MLOps (MLflow, Model Serving, TorchServe) rather than backend web development.

### Scenario 4: Limited Skill Resume
- Upload `data/sample_resumes/sam_taylor_minimal_resume.txt`.
- **Result:** Demonstrates how the system handles limited information gracefully, categorizing missing requirements into foundational beginner milestones without hallucinating qualifications.

---

## 🐳 Docker Deployment (Optional)

```bash
docker-compose up --build
```
Access the application at `http://localhost:8501`.
