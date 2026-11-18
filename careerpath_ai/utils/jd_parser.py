"""
Job description parser and repository of sample benchmark roles.
"""

import os
from typing import Dict, List
from utils.resume_parser import parse_pdf, parse_txt


def parse_jd_file(uploaded_file) -> str:
    """Parse uploaded Job Description file (PDF, TXT)."""
    filename = getattr(uploaded_file, "name", "").lower()
    if filename.endswith(".pdf"):
        return parse_pdf(uploaded_file)
    elif filename.endswith(".txt"):
        return parse_txt(uploaded_file)
    else:
        raise ValueError("Job descriptions must be uploaded as .txt or .pdf files.")


def get_sample_job_descriptions() -> Dict[str, str]:
    """Returns official benchmark job descriptions for the 7 standard engineering roles."""
    return {
        "Python Developer": """Role: Python Backend Developer
Company: Enterprise Cloud Solutions
Experience Required: 2-4 Years
Education: Bachelor's degree in Computer Science, Software Engineering or related field

Job Overview:
We are seeking an experienced Python Developer to build and maintain scalable backend services, high-throughput REST APIs, and database integrations.

Required Technical Skills:
- Python (Object-Oriented Programming, AsyncIO, Generators)
- Web Frameworks: FastAPI, Django, or Flask
- Database Systems: PostgreSQL, SQL query optimization, SQLAlchemy ORM
- API Design: RESTful APIs, JSON schema validation, OpenAPI/Swagger
- Testing: pytest, unit testing, integration testing
- Version Control: Git, GitHub collaboration, PR reviews
- OS: Linux environment and command line proficiency

Preferred Technical Skills:
- Docker containerization and Docker Compose
- Caching & Message Queues: Redis, Celery
- Cloud: AWS (EC2, S3, RDS)
- CI/CD: GitHub Actions or GitLab CI
- Microservices architecture

Key Responsibilities:
- Architect reliable backend microservices handling high concurrency
- Write maintainable, test-covered code adhering to PEP 8 standards
- Optimize complex database queries and prevent latency bottlenecks
- Partner with frontend engineers to deliver cohesive product features""",

        "Data Analyst": """Role: Data Analyst
Company: Insights & Analytics Global
Experience Required: 1-3 Years
Education: Bachelor's degree in Statistics, Mathematics, Computer Science, Economics or equivalent

Job Overview:
Seeking an analytical, detail-oriented Data Analyst to translate complex business data into clear, actionable executive insights and dashboards.

Required Technical Skills:
- Python: Pandas, NumPy, Data Cleaning, Data Transformation
- Advanced SQL: Window functions, CTEs, complex joins, data aggregation
- Visualization: Tableau, Power BI, or Matplotlib/Seaborn
- Statistical Analysis: Hypothesis testing, regression, descriptive statistics
- Excel: Advanced pivot tables, VLOOKUP/XLOOKUP, summary modeling
- Data Storytelling & Presentation: Clear communication of metrics to stakeholders

Preferred Technical Skills:
- Business Intelligence ETL workflows
- R programming for exploratory statistical computing
- Cloud Data Warehousing: Google BigQuery, Snowflake, or AWS Redshift
- Basic Machine Learning concepts (clustering, forecasting)
- Jupyter Notebooks for reproducible research

Key Responsibilities:
- Extract, clean, and validate data across multi-table relational databases
- Design interactive KPI executive dashboards tracking core business performance
- Identify behavioral trends, anomalies, and revenue optimization opportunities""",

        "Machine Learning Engineer": """Role: Machine Learning Engineer
Company: Cognitive AI Research Labs
Experience Required: 2-4 Years
Education: Master's or Bachelor's degree in Computer Science, Artificial Intelligence, or Data Science

Job Overview:
Looking for an applied Machine Learning Engineer to design, evaluate, and deploy predictive ML models and automated data pipelines into production systems.

Required Technical Skills:
- Python (Advanced numerical computing, vectorization)
- Core ML Frameworks: Scikit-learn, XGBoost, LightGBM
- Deep Learning: PyTorch or TensorFlow / Keras
- Data Pipeline & Preprocessing: Pandas, NumPy, Scipy
- Feature Engineering, Dimensionality Reduction, Outlier Detection
- Model Evaluation: ROC-AUC, Precision-Recall, Cross-validation, Bias-Variance analysis
- SQL & Relational Databases for dataset synthesis
- Git version control

Preferred Technical Skills:
- MLOps: MLflow, DVC, Weights & Biases
- Model Serving: TorchServe, Triton, ONNX Runtime, FastAPI
- Containerization: Docker, Kubernetes
- Cloud ML: AWS SageMaker, GCP Vertex AI
- Distributed Computing: Apache Spark, Ray

Key Responsibilities:
- Develop predictive classification, regression, and clustering algorithms
- Implement robust cross-validation pipelines preventing data leakage
- Benchmark and optimize model latency for low-overhead real-time inference""",

        "AI/ML Engineer": """Role: AI/ML Engineer (Generative AI & LLMs)
Company: NextGen Intelligence
Experience Required: 3-5 Years
Education: Degree in Computer Science, Artificial Intelligence, or Mathematics

Job Overview:
We are hiring an AI/ML Engineer specializing in Modern Generative AI, Large Language Models (LLMs), RAG architectures, and NLP pipeline engineering.

Required Technical Skills:
- Python (Expert proficiency)
- Deep Learning & NLP: PyTorch, Hugging Face Transformers, Tokenizers
- Generative AI & LLM Frameworks: LangChain, LangGraph, LlamaIndex
- Vector Databases: ChromaDB, FAISS, Pinecone, or Qdrant
- Retrieval-Augmented Generation (RAG) architecture and chunking strategies
- Prompt Engineering, Fine-tuning (LoRA, QLoRA), Model Quantization
- REST API deployment of AI endpoints using FastAPI
- Linux and Git version control

Preferred Technical Skills:
- Local LLM inference runtimes: Ollama, vLLM, TensorRT-LLM
- Multi-agent orchestration systems
- MLOps & LLMOps: Evaluation frameworks, TruLens, Ragas
- Docker & Kubernetes for GPU workloads
- Cloud Infrastructure: AWS or GCP GPU instances

Key Responsibilities:
- Architect resilient RAG systems combining semantic embeddings and rerankers
- Fine-tune open-weight models for specialized domain tasks
- Build production-ready multi-agent workflows with structured output validation""",

        "Java Developer": """Role: Java Backend Engineer
Company: Financial Enterprise Systems
Experience Required: 3-5 Years
Education: Bachelor's degree in Computer Science or Software Engineering

Job Overview:
Seeking a skilled Java Developer to build high-performance, fault-tolerant financial microservices using Spring Boot and cloud-native paradigms.

Required Technical Skills:
- Java (Java 17+, Core Java, Concurrency, Stream API)
- Frameworks: Spring Boot, Spring Data JPA, Spring Security
- RESTful Microservices architecture & API contracts
- Relational Databases: PostgreSQL, Oracle, MySQL, Hibernate ORM
- Build Tools: Maven or Gradle
- Unit Testing: JUnit 5, Mockito, AssertJ
- Version Control: Git

Preferred Technical Skills:
- Distributed Messaging: Apache Kafka, RabbitMQ
- Containers & Orchestration: Docker, Kubernetes
- Cloud: AWS, Azure
- In-memory Caching: Redis
- CI/CD: Jenkins, ArgoCD
- NoSQL: MongoDB

Key Responsibilities:
- Build robust microservices capable of processing millions of secure transactions
- Implement stringent unit and integration test suites achieving high coverage
- Collaborate in Agile sprints adhering to strict design pattern standards""",

        "Full Stack Developer": """Role: Full Stack Web Developer
Company: Agile Interactive Apps
Experience Required: 2-4 Years
Education: Bachelor's degree in Computer Science or equivalent practical experience

Job Overview:
We are looking for a versatile Full Stack Developer capable of building polished, responsive client web applications and high-performance server APIs.

Required Technical Skills:
- Frontend: JavaScript (ES6+), TypeScript, React.js (Hooks, Context, State Management)
- Web Core: HTML5, CSS3, Modern CSS (Tailwind CSS or Styled Components)
- Backend: Node.js (Express) or Python (FastAPI / Django)
- Database: PostgreSQL, MySQL, or MongoDB
- API Integration: RESTful APIs, Axios, Fetch, WebSockets
- Git version control and GitHub workflows

Preferred Technical Skills:
- Next.js (Server Components, SSR)
- GraphQL & Apollo Client
- Docker containerization
- CI/CD pipelines & Vercel / AWS deployment
- Automated testing (Jest, React Testing Library, Cypress)

Key Responsibilities:
- Implement responsive user interfaces with attention to accessibility and UX
- Develop secure, well-documented backend endpoints
- Optimize frontend web vitals and overall bundle size""",

        "DevOps Engineer": """Role: DevOps & Cloud Infrastructure Engineer
Company: Scalable Cloud Platforms
Experience Required: 2-5 Years
Education: Bachelor's in CS, IT, or equivalent industry experience

Job Overview:
Seeking a dedicated DevOps Engineer to automate infrastructure provisioning, enhance CI/CD delivery pipelines, and ensure cloud system reliability.

Required Technical Skills:
- Operating Systems: Linux / Unix administration, Shell Scripting (Bash)
- Containerization & Orchestration: Docker, Kubernetes, Helm Charts
- Infrastructure as Code (IaC): Terraform or Ansible
- CI/CD Automation: GitHub Actions, GitLab CI, or Jenkins
- Cloud Providers: AWS (EC2, VPC, IAM, EKS, CloudWatch) or Azure / GCP
- Networking Fundamentals: DNS, TCP/IP, Load Balancers, SSL/TLS certificates
- Git version control

Preferred Technical Skills:
- Monitoring & Observability: Prometheus, Grafana, ELK Stack / Datadog
- Security & Compliance: Vulnerability scanning (Trivy, SonarQube)
- Python or Go for infrastructure automation scripts
- Service Mesh (Istio) and GitOps (ArgoCD)

Key Responsibilities:
- Architect and maintain secure CI/CD pipelines enabling zero-downtime deployments
- Manage Kubernetes clusters across development, staging, and production
- Enforce infrastructure security, automated backups, and incident alerting"""
    }
