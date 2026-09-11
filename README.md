<div align="center">

# 🧠 DocuMind
### Retrieval-Augmented Document Intelligence Agent

*Upload a document. Ask a question. Get an answer that's grounded in the source — never invented.*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-6A5ACD?style=flat-square)
![Groq](https://img.shields.io/badge/LLM%20Inference-Groq-F55036?style=flat-square)
![Docker](https://img.shields.io/badge/Containerized-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square)

</div>

> *"An AI system's real value isn't in how confidently it answers — it's in how honestly it admits what it doesn't know."*
> — Engineering principle behind DocuMind's grounding strategy

---

## Quick Summary

- **Retrieval-grounded Q&A** — every answer is generated exclusively from the uploaded document's content; the LLM is contractually instructed to refuse when the answer isn't present.
- **Transparent trust signal** — a confidence score is *computed* from vector-distance math, not guessed by the model, so users know how strong the retrieval match actually was.
- **Full source traceability** — every answer names the exact source file it came from, and every Q&A pair is persisted to an auditable log.
- **Lean, intentional codebase** — the entire retrieval-augmented-generation pipeline runs in **209 lines of Python across 5 single-responsibility modules**.
- **Container-first delivery** — one `docker compose up` away from running, with secrets isolated to environment variables.

---

## Repository Structure

```
Documind/
├── .streamlit/
│   └── config.toml                 # UI theme (colors, font)
├── backend/
│   ├── __init__.py
│   ├── config.py                   # env vars, cached resources (embedder, vector DB, LLM client)
│   ├── rag.py                      # ingest → chunk → embed → retrieve
│   ├── llm.py                      # prompt construction + grounded generation
│   └── audit.py                    # Q&A history: save / list / clear
├── frontend/
│   └── app.py                      # Streamlit chat UI (upload, chat, avatars, metrics)
├── Demo/
│   ├── 01_end_to_end_pipeline.gif
│   ├── documind_architecture_showcase.gif
│   └── documind_live_demo.webm
├── diagram_pngs/
│   └── architecture_flow.png       # ← add your architecture diagram here
├── screenshots/
│   └── *.png                       # ← add your UI screenshots here
├── data/                           # runtime-only: chroma index, uploads, audit log (git-ignored)
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Table of Contents

- [Overview](#overview)
- [See It In Action](#see-it-in-action)
- [The Problem It Solves](#the-problem-it-solves)
- [Architecture](#architecture)
- [Engineering Decisions](#engineering-decisions)
- [Skills and Competencies Demonstrated](#skills-and-competencies-demonstrated)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Proof It Works](#proof-it-works)
- [Scaling to Production](#scaling-to-production)

---

## Overview

DocuMind is a **Retrieval-Augmented Generation (RAG) agent**: a document is ingested, split into overlapping text chunks, embedded into vectors, and indexed in a local vector store. When a user asks a question, the system retrieves the most semantically relevant chunks, assembles them into a bounded context window, and hands that context — and only that context — to an LLM for answer generation. Every answer carries a computed confidence score and a named source, and every exchange is written to a persistent audit trail.

The system is deliberately small: five Python modules, each with one job, wired together through a Streamlit chat interface.

---

## See It In Action

**1. End-to-end pipeline**

![End-to-end pipeline demo](Demo/01_end_to_end_pipeline.gif)

**2. Architecture showcase**

![Architecture showcase](Demo/documind_architecture_showcase.gif)

**3. Live application walkthrough**

<video src="Demo/documind_live_demo.webm" controls width="100%"></video>

*(If the video doesn't render inline on your platform, [open it directly](Demo/documind_live_demo.webm).)*

---

## The Problem It Solves

| Without This Workflow | With DocuMind |
|---|---|
| Manually skim a PDF/TXT to find an answer | Ask in plain English, get a direct answer |
| No way to verify an AI's claim against the source document | Every answer cites the exact source file it was pulled from |
| Generic LLM answers can drift from — or invent beyond — the document | The prompt contract restricts generation to retrieved context only, and the model is instructed to say so when context is insufficient |
| No sense of how "sure" an answer is | A numeric confidence score, derived from vector-similarity distance, is shown on every answer |
| No record of what was asked or answered | Every Q&A pair is persisted to an audit log, reviewable or clearable on demand |

---

## Architecture

![Architecture Diagram](diagram_pngs/architecture_flow.png)

**Pipeline flow:**

```
Upload (PDF/TXT)
   │
   ▼
Text Extraction (pypdf for PDFs)
   │
   ▼
Chunking (800 chars, 120-char overlap)
   │
   ▼
Embedding (fastembed · BAAI/bge-small-en-v1.5)
   │
   ▼
Vector Store (ChromaDB, persistent local collection)
   │
   ▼
Query → Embed → Similarity Search (top-6) → Confidence Score
   │
   ▼
Context Assembly → Groq LLM (openai/gpt-oss-120b)
   │
   ▼
Grounded Answer + Source + Confidence → Audit Log (JSON)
```

---

## Engineering Decisions

- **Single active-document indexing.** Uploading a new file clears prior vectors before re-indexing. This deliberately scopes retrieval to one document at a time, eliminating cross-document bleed-through in exchange for architectural simplicity.
- **Computed, not claimed, confidence.** The confidence score is derived mathematically from vector-query distance (`1 − avg(distance)`), giving a deterministic, explainable trust signal instead of asking the LLM to self-rate its own certainty.
- **Guardrail-routed retrieval.** Aggregate-style questions ("how many," "compare," "list all," etc.) bypass top-k similarity search entirely and pull the full indexed context — because averaging or counting across a document needs everything, not just the closest match.
- **Prompt-contract grounding.** The LLM is explicitly instructed to answer using *only* the supplied context and to say so when the answer isn't present — a direct, low-overhead guardrail against fabricated answers.
- **Graceful degradation.** LLM/API failures are caught and surfaced as a clear, user-facing message instead of crashing the session.
- **Secrets never touch source.** The API key is read exclusively from the environment; the app hard-stops with an explicit Streamlit error if it's missing, rather than failing silently downstream.
- **Disposable runtime state.** The vector index, uploaded files, and audit log all live under `data/` and are excluded from version control — treated as regenerable session state, not as source of truth.
- **Resource caching by design.** The embedding model, vector collection, and LLM client are wrapped in `@st.cache_resource` so they initialize once, not on every Streamlit rerun.

---

## Skills and Competencies Demonstrated

**AI / Machine Learning Engineering**
- Retrieval-Augmented Generation (RAG) pipeline design end-to-end
- Text chunking strategy with overlap tuning for retrieval quality
- Embedding model integration (`fastembed`, `BAAI/bge-small-en-v1.5`)
- Vector similarity search and distance-based confidence scoring
- Prompt engineering with explicit grounding constraints to reduce hallucination

**Backend Engineering**
- Modular, single-responsibility architecture (5 focused modules, zero monolith)
- Environment-driven configuration and secret management
- Persistent local audit logging (JSON-based event trail)
- Defensive error handling around third-party API calls

**Frontend / Product Engineering**
- Real-time chat UI built in Streamlit (session state, avatars, live toasts)
- UX-conscious feedback design (contextual first-run message, confidence badges, progressive disclosure)

**DevOps / Delivery**
- Containerization with Docker and Docker Compose (volume-mounted persistent data)
- Reproducible, dependency-pinned environments (`requirements.txt`)
- Clean separation of runtime artifacts from source control via `.gitignore`

**Methodology**
DocuMind was built around one constraint: *constrain the model before you trust it.* Rather than relying on a large general-purpose assistant to "figure it out," every architectural choice — chunk size, retrieval routing, prompt contract, confidence computation — exists to narrow the system's behavior into something predictable, auditable, and explainable. This is the difference between a demo that *feels* smart and a system a business can actually rely on: concrete engineering guardrails, not model size, are what make an AI feature trustworthy in production.

---

## Tech Stack

| Layer | Tool | Role |
|---|---|---|
| Frontend / UI | Streamlit | Chat interface, file upload, session state, live feedback |
| Application Runtime | Python 3.11 | Core orchestration logic across all modules |
| Embedding Model | fastembed (`BAAI/bge-small-en-v1.5`) | Converts text chunks and queries into vectors |
| Vector Store | ChromaDB (persistent client) | Stores and queries document embeddings locally |
| LLM Inference | Groq API (`openai/gpt-oss-120b`) | Generates grounded answers from retrieved context |
| Document Parsing | pypdf | Extracts text from uploaded PDFs |
| Configuration | python-dotenv | Loads environment variables from `.env` |
| Containerization | Docker · Docker Compose | Reproducible build and runtime, with volume-mounted data |
| Observability | Custom JSON audit log | Persists every question, answer, source, and confidence score |

---

## Getting Started

### 1. Import the Project
```cmd
git clone <your-repo-url>
cd Documind
```

### 2. Configure Credentials

| Variable | Required | Where to Get It | Notes |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | https://console.groq.com/keys | Free tier available, no card required |
| `DATA_DIR` | No | — | Defaults to `./data` if unset |

### 3. Set Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
DATA_DIR=./data
```

### 4. Smoke Test

**Option A — Docker:**
```cmd
docker compose up --build
```

**Option B — Local Python:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run frontend/app.py
```

Then open **http://localhost:8501** — upload a PDF or TXT file and ask it a question. A successful smoke test looks like: file indexed → toast confirmation → a chat answer with a visible confidence badge and source citation.

---

## Proof It Works

<details>
<summary><strong>Click to expand application screenshots</strong></summary>

![Chat interface](screenshots/chat-interface.png)
![Document upload and indexing](screenshots/upload-indexing.png)
![Confidence score and source citation](screenshots/confidence-source.png)

</details>

---

## Scaling to Production

| Aspect | Proof of Concept (Current) | Production Plan |
|---|---|---|
| Audit Log | Flat JSON file | Managed relational database with indexed, queryable history |
| Document Scope | One active document at a time (re-indexed on upload) | Multi-document, multi-tenant collections with namespacing |
| Authentication | None | Native `st.login` / SSO integration |
| Secrets | `.env` file | Managed secrets store (cloud provider secrets manager) |
| Deployment | Single container via Docker Compose | Orchestrated deployment (e.g., Kubernetes) with autoscaling behind a load balancer |
| Observability | Console logging + JSON audit trail | Structured logging with metrics and distributed tracing |
| Vector Store | Local persistent ChromaDB | Managed or distributed vector database |

---

<div align="center">

**Author:** *(add your name, portfolio link, and contact here)*

</div>
