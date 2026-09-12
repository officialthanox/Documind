
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

**AI/ML Engineering**
- Retrieval-Augmented Generation (RAG) pipeline design end-to-end
- Text chunking strategy with overlap tuning for retrieval quality
- Vector similarity search and distance-based confidence scoring
- Prompt engineering with explicit grounding constraints to reduce hallucination
- Retrieval routing (guardrail logic for aggregate-style queries)

**LLM & APIs**
- Groq API integration (`openai/gpt-oss-120b`)
- Prompt-contract design for grounded, hallucination-resistant generation

**Backend Engineering**
- Modular, single-responsibility architecture (5 focused modules, zero monolith)
- Environment-driven configuration and secrets management
- Defensive error handling around third-party API calls

**Data & Storage**
- ChromaDB (persistent local vector store)
- pypdf (PDF text extraction)
- JSON-based audit trail persistence

**Frontend / Product**
- Real-time chat UI built in Streamlit (session state, avatars, live toasts)
- UX-conscious feedback design (contextual first-run message, confidence badges, progressive disclosure)

**DevOps / Delivery**
- Containerization with Docker and Docker Compose (volume-mounted persistent data)
- Reproducible, dependency-pinned environments (`requirements.txt`)
- Clean separation of runtime artifacts from source control via `.gitignore`

**Methodology**

DocuMind was built around one constraint: *constrain the model before you trust it.* Rather than relying on a large general-purpose assistant to "figure it out," every architectural choice — chunk size, retrieval routing, prompt contract, confidence computation — exists to narrow the system's behavior into something predictable, auditable, and explainable. This is the difference between a demo that feels smart and a system a business can actually rely on: concrete engineering guardrails, not model size, are what make an AI feature trustworthy in production.

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

## Author

**Thanojan Sivasuntharam**
Aspiring AI Engineer · RAG & LLM Systems

📧 [officialthanox@gmail.com](mailto:officialthanox@gmail.com) · 🔗 [LinkedIn](https://linkedin.com/in/nevin-thanox) · 💻 [GitHub](https://github.com/officialthanox/Documind)

<div align="center">

*Trust here is architectural, not cosmetic.*

</div>
