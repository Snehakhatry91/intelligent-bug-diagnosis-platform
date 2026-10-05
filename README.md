# Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3-purple.svg)](https://vite.dev)
[![Pytest](https://img.shields.io/badge/Pytest-25%2F25%20Passed-emerald.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous software engineering diagnostic platform that accelerates defect triage, extracts crash signals deterministically, searches historical defect corpora (Mozilla, Apache, Eclipse) via 384-dimensional dense semantic vector similarity (`sentence-transformers/all-MiniLM-L6-v2`), identifies duplicates, formulates anti-hallucinated root cause hypotheses, and generates actionable code-fix recommendations, example patches, and automated test plans.

**Organization**: Infosys Internship Evaluation Project  
**Copyright**: Copyright (c) 2025 Vidzai Digital. MIT License.

---

## Overview

Modern software development teams face severe operational bottlenecks when triaging, diagnosing, and resolving production defects. Software bug reports are often incomplete, duplicate filings go unnoticed, and root-cause analyses require extensive manual investigation across complex distributed architectures.

The **Intelligent Bug Diagnosis Platform** combines transformer-based semantic retrieval with deterministic heuristic reasoning for reproducible offline diagnosis. Optional local Ollama-based LLM assistance can be configured where supported. The system is designed to be 100% locally runnable, cost-free, and reproducible without external paid APIs.

---

## Problem Statement

1. **High Mean Time to Detect (MTTD) & Resolve (MTTR)**: Engineers spend excessive hours reconstructing stack traces and deciphering cryptic failure logs.
2. **Duplication Fatigue**: Up to 30% of filed issues in enterprise systems are duplicate or closely related defects.
3. **AI Hallucinations in Automated Tooling**: Generative AI tools frequently invent fake stack traces, non-existent libraries, or fictitious upstream ticket citations.
4. **Data Integrity & Traceability**: Automated systems often lack genuine historical evidence links with verifiable provenance.
5. **Operational Fragility**: Systems relying on external cloud APIs suffer from unpredictable downtime, rate limiting, and reproducibility failures during evaluation.

---

## Key Features

- **Multi-Agent Orchestration**: Five specialized agents executing in a canonical pipeline with graceful fault isolation.
- **Deterministic Log Analysis**: Deterministic AST and regex parser extracting exception types, failing frames, and file paths across Java, Python, Node.js, and Unix signals without hallucinated frames.
- **Curated Historical Knowledge Base**: Provenance-linked historical defect records from Mozilla Bugzilla, Apache Jira, and Eclipse Bugzilla with verified upstream URLs and project-curated resolution summaries.
- **Dense Semantic Embeddings**: Powered by local open-source `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional unit vectors.
- **Single Centralized Similarity Policy**: Exact cosine similarity with unified threshold gating:
  - $\ge 0.82$: **Likely Duplicate**
  - $0.65 - 0.81$: **Related Issue**
  - $0.45 - 0.64$: **Weak Match**
  - $< 0.45$: **Insufficient Historical Evidence**
- **Strict Anti-Hallucination Policy**: Four-tier attribution separating observed facts from AI inferences. If similarity is $< 0.45$, returns `"Insufficient historical evidence found"` without fabricating citations.
- **Knowledge Base Growth**: Human-in-the-loop candidate promotion workflow before new defects enter the active vector index.
- **Reconciled Analytics Telemetry**: Mathematical integrity checks ensuring sum of category distributions equals total population ($\sum Counts \equiv Total$).
- **Offline & Reproducible**: Fully local execution; no API keys required for core functionality.
- **Deterministic Reasoning with Optional LLM**: Default signal/rule-based reasoning for 100% offline reproducibility, with optional local open-weight Ollama (`llama3:8b`) integration where configured.

---

## Architecture

```
Bug Submission (Text, Stack Trace, or 5MB File Upload)
                     │
                     ▼
             [Triage Agent]
         (Severity, Priority, Component)
                     │
                     ▼
          [Log Analysis Agent]
   (Deterministic Java, Python, Node, Signals)
                     │
                     ▼
         [Canonical Data Model]
          (BugAnalysisContext)
                     │
                     ▼
         [RAG Retrieval Engine]
   (384-dim Dense Vector Semantic Search)
   (Mozilla, Apache, Eclipse Defect Corpora)
                     │
                     ▼
     [Duplicate Detection Agent]
     (Centralized >= 0.82 Gating)
                     │
                     ▼
          [Root Cause Agent]
  (4-Tier Attribution: Facts, Evidence, Inference)
                     │
                     ▼
         [Remediation Agent]
   (Actionable Recommendations & Tests)
                     │
                     ▼
        [Structured Findings UI]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 [Defect Analytics]    [Verified KB Growth]
  (Reconciled ∑=N)      (Human Verification)
```

---

## Five Specialized Agents

The platform coordinates five specialized, single-responsibility agents through `agents/orchestrator.py`:

1. **Triage Agent** (`agents/triage_agent.py`): Evaluates defect severity, business priority, and affected system component using signal-based heuristic rules.
2. **Log Analysis Agent** (`agents/log_analysis_agent.py`): Deterministically regex-parses execution traces into structured `StackFrame` and exception objects without hallucinated frames.
3. **Duplicate Detection Agent** (`agents/duplicate_detection_agent.py`): Compares dense embeddings against indexed historical defects using the centralized similarity policy ($\ge 0.82$ duplicate threshold).
4. **Root Cause Agent** (`agents/root_cause_agent.py`): Combines observed facts and retrieved historical evidence into a grounded causal hypothesis using Four-Tier Fact Attribution.
5. **Remediation Agent** (`agents/remediation_agent.py`): Formulates actionable code-fix recommendations, example patch diffs, and verification test specifications.

*(The RAG Retrieval Engine in `rag/retrieval_engine.py` serves as the underlying semantic retrieval service supporting the agents).*

---

## RAG Pipeline

```
Bug Report / Crash Log
        ↓
Text Normalization & Chunking
        ↓
SentenceTransformer Embedding ('all-MiniLM-L6-v2')
        ↓
384-Dimensional Dense Vector
        ↓
Persistent Vector Store (rag/vector_index.pkl)
        ↓
Exact Cosine Similarity Comparison
        ↓
Evidence Threshold Filtering (>= 0.45)
        ↓
Top-K Historical Evidence Matches
```

- **Current Evaluation Implementation**: For the current evaluation prototype, historical defect embeddings are stored in a persistent local vector index (`rag/vector_index.pkl`) and compared using cosine similarity via NumPy.
- **Production Scaling Option**: The architecture can be migrated to PostgreSQL/pgvector or another vector database (such as Qdrant or Milvus) for larger-scale deployment.

---

## Historical Knowledge Base

The platform ships with curated, provenance-linked public defects sourced from three major open-source ecosystems:
- **Mozilla Bugzilla**: Core networking, layout memory leaks, and SpiderMonkey deadlocks (`MOZ-12870`, `MOZ-120`, `MOZ-32992`, `MOZ-7531`, `MOZ-1434`).
- **Apache Jira**: Kafka consumer rebalances, Cassandra SSTable OOMs, and HttpComponents socket timeouts (`KAFKA-10134`, `KAFKA-897`, `CASSANDRA-19564`, `HTTPCLIENT-2099`, `CASSANDRA-2189`).
- **Eclipse Bugzilla**: Workbench deadlocks, build NPEs, and repository authentication errors (`ECLIPSE-3322`, `ECLIPSE-11303`, `ECLIPSE-4869`, `ECLIPSE-3128`, `ECLIPSE-5226`).

Each historical record contains verified source provenance:
```json
{
  "id": "MOZ-12870",
  "project": "Mozilla",
  "source": "Mozilla Bugzilla",
  "source_issue_id": "12870",
  "source_url": "https://bugzilla.mozilla.org/show_bug.cgi?id=12870",
  "title": "AB-BA deadlocks between pipe and channel critical sections",
  "description": "Deadlock occurs between nsPipe and nsHttpChannel when...",
  "component": "Networking",
  "resolution": "FIXED",
  "resolution_summary": "Reordered lock acquisition protocol between transport pipe and HTTP transaction monitor.",
  "verified": true,
  "data_type": "historical"
}
```

*Note on Data Integrity:* Historical issue fields (`id`, `source`, `source_issue_id`, `source_url`, `title`, `description`, `component`, `resolution`) are directly linked to public upstream trackers, while resolution and fix summaries (`resolution_summary`, `fix_patch_summary`) are curated by the project to provide concise diagnostic context.

The five demo scenarios are explicitly partitioned with `"synthetic_demo": true` and `"data_type": "synthetic"` to exercise the complete pipeline.

---

## Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384
- **Normalization**: Unit L2 sphere ($\|\mathbf{v}\|_2 = 1.0$)
- **Similarity Metric**: Cosine similarity ($\mathbf{u} \cdot \mathbf{v}$)
- **Runtime**: Local CPU execution; no external API key, zero cost, completely reproducible.

---

## Duplicate Detection

Centralized threshold policy configured in `backend/config.py`:
- **$\ge 0.82$**: **Likely Duplicate** (Surfaces historical fix and prevents redundant defect filing)
- **$0.65 - 0.81$**: **Related Issue** (Shared component or subsystem; suggests known workarounds)
- **$0.45 - 0.64$**: **Weak Match** (Distantly related architectural context)
- **$< 0.45$**: **Insufficient Historical Evidence** (Treated as novel defect)

---

## Root Cause Analysis

Enforces strict four-tier attribution:
1. **OBSERVED FACTS**: Deterministically extracted from the submitted error message and stack trace.
2. **HISTORICAL EVIDENCE**: Grounded citations from retrieved vector store records.
3. **AI INFERENCE**: Clearly flagged deductive reasoning on failure propagation.
4. **FIX RECOMMENDATION**: Actionable engineering remedy.

Wording strictly distinguishes `"Observed Facts"` from `"Likely"` inferences and `"Historical evidence suggests"`.

---

## Remediation

Formulates actionable code-fix recommendations, example patch diffs, and verification test specifications:
- Specific remediation action and technical rationale
- Concrete unified diff example code patch
- Automated unit/integration test specifications
- Implementation guidance and affected file paths

---

## Analytics

- Reconciled population metrics: $\sum(\text{Category Counts}) \equiv \text{Total Population}$.
- Explicitly separates user submissions, verified KB entries, and historical defect corpus.
- If no submissions exist, displays clear "No data available" states rather than fabricated numbers.

---

## Security

- Maximum upload size ceiling: **5 MB**
- Allowed file extensions: `.txt`, `.log`, `.md`, `.json`
- Input sanitization: Strips null bytes (`\x00`) and control characters
- UTF-8 byte validation
- Zero-execution policy: Uploaded files are strictly parsed as text and never executed
- Zero hardcoded secrets, passwords, or committed API keys

---

## Technology Stack

| Layer | Technology | Usage in Platform |
| :--- | :--- | :--- |
| **Backend** | Python 3.12, FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST API and pipeline orchestration |
| **Database** | SQLite + `aiosqlite` via SQLAlchemy 2.0 (async), `greenlet` | Asynchronous local relational storage for submissions and KB entries |
| **ML & Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`), PyTorch, NumPy | Dense 384-dimensional vector embedding generation on CPU |
| **Vector Store** | In-Memory NumPy Cosine Vector Engine | Persistent local binary index (`rag/vector_index.pkl`) with versioning |
| **Reasoning Engine** | Deterministic Heuristic Engine (Default) | Transparent rule-based reasoning; optional local Ollama integration |
| **Frontend** | React 18, TypeScript, Vite 8, Tailwind CSS, Recharts | Modern developer interface with real-time analytics visualizations |
| **Testing & CI** | Pytest, pytest-asyncio, GitHub Actions | Automated test suite and hermetic CI pipeline |

---

## Project Structure

```
intelligent-bug-diagnosis-platform/
├── backend/
│   ├── api/                  # FastAPI REST endpoints
│   ├── models/               # Pydantic schemas & SQLAlchemy ORM models
│   ├── services/             # Submission, analytics, and orchestrator services
│   ├── config.py             # Centralized settings & similarity thresholds
│   ├── database.py           # Async database engine & session maker
│   └── main.py               # FastAPI application entrypoint
├── agents/
│   ├── orchestrator.py       # Multi-agent DAG controller
│   ├── triage_agent.py       # Severity & priority triage
│   ├── log_analysis_agent.py # Deterministic stack trace parser
│   ├── root_cause_agent.py   # 4-tier root cause attribution
│   ├── duplicate_detection_agent.py # Centralized duplicate gating
│   ├── remediation_agent.py  # Code patch & test recommendation
│   └── llm_provider.py       # Deterministic fallback & Ollama provider
├── rag/
│   ├── embedder.py           # SentenceTransformer (all-MiniLM-L6-v2)
│   ├── vector_store.py       # Persistent vector index & cosine search
│   ├── retrieval_engine.py   # Anti-hallucination retrieval service
│   ├── text_chunker.py       # Domain-aware text chunking
│   └── kb_growth_manager.py  # Human verification promotion workflow
├── data/
│   ├── historical_bugs.json  # 15 verified historical records
│   ├── mozilla_bugs.json     # 5 verified Mozilla Bugzilla records
│   ├── apache_bugs.json      # 5 verified Apache Jira records
│   ├── eclipse_bugs.json     # 5 verified Eclipse Bugzilla records
│   └── validation_dataset.json # 10 labeled ground-truth evaluation cases
├── reports/
│   └── latest_evaluation.json# Machine-readable evaluation report
├── scripts/
│   ├── validate_historical_data.py # Historical dataset integrity & provenance validator
│   ├── ingest_historical_data.py   # Ingestion & vector indexing pipeline
│   ├── evaluate_agents.py          # Empirical evaluation benchmark
│   ├── run_demo_scenarios.py       # 5 synthetic demo scenarios runner
│   └── verify_project.py           # 11-step master reproducibility check
├── frontend/
│   ├── src/pages/            # Dashboard, Submit, Findings, Analytics, KB, Evaluation
│   └── src/api/client.ts     # Typed API client
└── tests/                    # 25 automated unit & integration tests
```

---

## Installation

```bash
# 1. Clone repository
git clone https://github.com/Snehakhatry91/intelligent-bug-diagnosis-platform.git
cd intelligent-bug-diagnosis-platform

# 2. Configure environment (optional custom settings)
cp .env.example .env

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd frontend
npm install
cd ..
```

---

## Running Backend

```bash
# Initialize Historical Knowledge Base and Vector Index
python scripts/validate_historical_data.py
python scripts/ingest_historical_data.py

# Start Backend Server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

---

## Running Frontend

```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Running Tests

```bash
python -m pytest tests -v
```
**Status: 25 passed in ~16s (100% Pass Rate)**

---

## Running Evaluation

```bash
python scripts/evaluate_agents.py
```
Outputs machine-readable metrics to `reports/latest_evaluation.json` and updates `docs/evaluation-report.md`.

---

## Running Demo Scenarios

```bash
python scripts/run_demo_scenarios.py
```
Executes the five mandatory synthetic demonstration scenarios end-to-end:
1. `DEMO-01`: NullPointerException Dereference (High Severity, Novel Defect)
2. `DEMO-02`: Database Connection Pool Saturated Deadlock (Critical Severity, Novel Defect)
3. `DEMO-03`: JWT Bearer Authentication Token Expiration (Medium Severity, Novel Defect)
4. `DEMO-04`: Network Socket Timeout on External API (High Severity, Weak Match correlation to HTTPCLIENT-2099)
5. `DEMO-05`: OutOfMemory Heap Exhaustion in Document Indexing (High Severity, Weak Match correlation to CASSANDRA-2189)

---

## Reproducibility

Execute the single comprehensive 11-step master verification gate:
```bash
python scripts/verify_project.py
```

Expected output:
```text
===================================
PROJECT VERIFICATION
===================================
Environment       : PASS
Dependencies      : PASS
Historical KB     : PASS
Embedding Model   : PASS
Vector Index      : PASS
RAG Retrieval     : PASS
Unit Tests        : PASS
Agent Evaluation  : PASS
Demo Scenarios    : PASS
API Verification  : PASS
Frontend Build    : PASS
-----------------------------------
Overall           : PASS
===================================
```

---

## Evaluation Results

*Evaluation on the project's 10-case internal validation dataset (recorded in reports/latest_evaluation.json via scripts/evaluate_agents.py):*

| Metric | Empirical Value | Sample Size | Derivation |
| :--- | :--- | :--- | :--- |
| **Severity Classification Accuracy** | **80.0%** | 10 | 8 / 10 ground-truth matches |
| **Priority Classification Accuracy** | **80.0%** | 10 | 8 / 10 ground-truth matches |
| **Duplicate Detection Accuracy** | **80.0%** | 10 | 8 / 10 correct binary calls |
| **Duplicate Detection Precision** | **100.0%** | 3 Positives | $\text{TP}/(\text{TP} + \text{FP}) = 3 / (3 + 0)$ |
| **Duplicate Detection Recall** | **60.0%** | 5 Actuals | $\text{TP}/(\text{TP} + \text{FN}) = 3 / (3 + 2)$ |
| **Duplicate Detection F1-Score** | **75.0%** | 10 | Harmonic mean of Precision and Recall |

### Duplicate Detection Confusion Matrix

| Actual \ Predicted | Predicted Duplicate ($\ge 0.82$) | Predicted Novel / Non-Duplicate ($< 0.82$) | Total Actual |
| :--- | :--- | :--- | :--- |
| **Actual Duplicate** | **3** (TP) | **2** (FN) | **5** |
| **Actual Non-Duplicate** | **0** (FP) | **5** (TN) | **5** |
| **Total Predicted** | **3** | **7** | **10** |

---

## Limitations

1. **Curated KB Size**: The prototype knowledge base contains 15 curated public defect records from Mozilla, Apache, and Eclipse; enterprise deployments require continuous synchronization with active bug trackers.
2. **Deterministic Fallback Scope**: In offline mode without Ollama, causal hypotheses are drawn from deterministic heuristic templates rather than open-ended neural generation.
3. **Local Vector Indexing**: The prototype uses an in-memory NumPy vector matrix with pickle persistence (`rag/vector_index.pkl`), suitable for hermetic local testing but needing a dedicated vector database (e.g. `pgvector` or Qdrant) at billion-scale.
4. **Duplicate Recall Trade-off**: Under strict thresholding ($\ge 0.82$), precision is 100% (zero false duplicates), but recall is 60% on edge cases with divergent phrasing.
5. **Log Obfuscation**: The deterministic parser expects unminified stack traces; minified client JavaScript or obfuscated bytecode requires source-map / ProGuard de-obfuscation.
6. **Synthetic Demo Scenarios**: The five demo scenarios are explicitly synthetic test cases designed to exercise the complete pipeline.
7. **Internal Validation Benchmark**: The empirical evaluation uses an internal 10-case validation benchmark designed to verify functional pipeline correctness rather than representing large-scale statistical production surveys.

---

## Future Improvements

1. **Larger Verified Historical KB**: Ingest tens of thousands of verified historical issues from additional ecosystems.
2. **pgvector / Qdrant Migration**: Transition vector store to distributed vector engines for billion-scale retrieval.
3. **Richer LLM Reasoning**: Enhanced prompt engineering and fine-tuned open-source coding models for complex multi-file architectural defects.
4. **Automatic Upstream Synchronization**: Scheduled sync jobs importing new resolved tickets from GitHub Issues and Jira.
5. **Human Feedback Loop**: Feedback ranking mechanisms allowing engineers to rate remediation patch quality.
6. **Confidence Calibration**: Platt scaling and temperature scaling to calibrate confidence estimates against empirical accuracy.
7. **Production Observability**: OpenTelemetry distributed tracing and Prometheus/Grafana metrics.
8. **Distributed Deployment**: Containerized Kubernetes deployment with horizontal pod autoscaling.
9. **Authentication & RBAC**: Enterprise OAuth2 / OpenID Connect integration for multi-tenant organizations.
10. **Expanded Benchmark Dataset**: Extend validation ground truth from 10 cases to 500+ diverse real-world software crashes.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2025 Vidzai Digital.
