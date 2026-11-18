"""
Deterministic and NLP-assisted skill extractor.
Combines comprehensive taxonomy regex extraction with spaCy NER (if present)
to guarantee accurate, verifiable skill detection from resumes.
"""

import re
from typing import Dict, List, Set, Any


TAXONOMY = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "php", "r",
        "scala", "perl", "bash", "shell", "powershell", "sql", "html", "css"
    ],
    "frameworks": [
        "fastapi", "django", "flask", "spring", "spring boot", "react", "react.js",
        "angular", "vue", "vue.js", "node.js", "express", "next.js", "nuxt.js",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
        "numpy", "scipy", "matplotlib", "seaborn", "plotly", "opencv", "spacy",
        "nltk", "huggingface", "transformers", "langchain", "langgraph",
        "llamaindex", "streamlit", "gradio", "tailwind", "bootstrap"
    ],
    "tools_platforms": [
        "git", "github", "gitlab", "docker", "kubernetes", "k8s", "jenkins",
        "github actions", "gitlab ci", "terraform", "ansible", "aws", "gcp",
        "azure", "linux", "unix", "postman", "swagger", "tableau", "power bi",
        "jupyter", "jupyter notebook", "colab", "kafka", "rabbitmq", "celery",
        "redis", "prometheus", "grafana", "mlflow", "wandb", "dvc"
    ],
    "databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "oracle",
        "sql server", "cassandra", "dynamodb", "redis", "chromadb", "faiss",
        "pinecone", "qdrant", "snowflake", "bigquery"
    ],
    "concepts": [
        "machine learning", "deep learning", "artificial intelligence",
        "natural language processing", "nlp", "computer vision", "cv",
        "generative ai", "llm", "large language models", "rag", "retrieval augmented generation",
        "data science", "data analysis", "data engineering", "rest api", "restful",
        "microservices", "ci/cd", "continuous integration", "agile", "scrum",
        "object oriented programming", "oop", "unit testing", "system design"
    ],
    "soft_skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "collaboration", "adaptability", "time management",
        "mentoring", "presentation", "analytical skills"
    ]
}


def extract_skills_nlp(text: str) -> Dict[str, List[str]]:
    """Extract skills deterministically using keyword boundary regex."""
    text_lower = text.lower()
    extracted = {k: [] for k in TAXONOMY}

    for category, terms in TAXONOMY.items():
        for term in terms:
            # Word boundary regex ensuring punctuation doesn't block matches
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
            if re.search(pattern, text_lower):
                extracted[category].append(term.title() if len(term) > 3 else term.upper())

    return extracted


def extract_skills_with_spacy(text: str) -> Dict[str, List[str]]:
    """Extract skills utilizing spaCy NER if available, falling back gracefully."""
    results = extract_skills_nlp(text)
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ("PRODUCT", "ORG"):
                    e_text = ent.text.strip().lower()
                    for cat, terms in TAXONOMY.items():
                        if e_text in terms:
                            val = e_text.title()
                            if val not in results[cat]:
                                results[cat].append(val)
        except Exception:
            pass
    except ImportError:
        pass

    return results


def get_all_candidate_skills(resume_analysis: Dict[str, Any]) -> List[str]:
    """Compile a deduplicated flat list of all candidate skills found across all sections."""
    skills = set()

    for s in resume_analysis.get("technical_skills", []):
        if isinstance(s, dict):
            skills.add(s.get("name", "").strip())
        elif isinstance(s, str):
            skills.add(s.strip())

    for s in resume_analysis.get("soft_skills", []):
        if isinstance(s, dict):
            skills.add(s.get("name", "").strip())
        elif isinstance(s, str):
            skills.add(s.strip())

    for key in ["programming_languages", "frameworks_libraries", "tools_platforms", "databases"]:
        for item in resume_analysis.get(key, []):
            if isinstance(item, str) and item.strip():
                skills.add(item.strip())

    # Add technologies embedded inside project and experience objects
    for proj in resume_analysis.get("projects", []):
        if isinstance(proj, dict):
            for t in proj.get("technologies", []):
                skills.add(str(t).strip())

    for exp in resume_analysis.get("experience", []):
        if isinstance(exp, dict):
            for t in exp.get("technologies", []):
                skills.add(str(t).strip())

    return sorted([s for s in skills if s])
