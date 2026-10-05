# System Architecture & Technical Specification

## Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance
**Organization:** Infosys Internship Evaluation Project  
**Author:** Software Architect & Engineering Lead  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. High-Level Architecture Overview

The Intelligent Bug Diagnosis Platform is structured as an asynchronous micro-architecture combining deterministic AST/regex parsers, an agentic reasoning Directed Acyclic Graph (DAG), and a dense vector Retrieval-Augmented Generation (RAG) knowledge engine grounded in curated open-source defect repositories from Mozilla, Apache, and Eclipse.

```
+---------------------------------------------------------------------------------------------------+
|                                  Developer / QA User (Web UI)                                     |
|  - Modern Dark Theme (Tailwind CSS)                                                               |
|  - Real-Time Dynamic Charts (Recharts)                                                            |
|  - Single-Page Multi-View Navigation (Dashboard, Submit, Results, Historical, Analytics, KB)      |
+-------------------------------------------------+-------------------------------------------------+
                                                  | REST / JSON
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                      FastAPI Backend Engine                                       |
|                                                                                                   |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
|  | Request Sanitization &    |   | Deterministic Log &       |   | Multi-Agent Orchestrator    |  |
|  | File Upload Validator     |   | Stack Trace Parser        |   | (Async State Machine)       |  |
|  +-------------+-------------+   +-------------+-------------+   +--------------+--------------+  |
|                |                               |                                |                 |
|                v                               v                                v                 |
|  +---------------------------------------------------------------------------------------------+  |
|  |                                  Canonical Data Model                                       |  |
|  |                                  (BugAnalysisContext)                                       |  |
|  +---------------------------------------------------------------------------------------------+  |
|                |                               |                                |                 |
|                v                               v                                v                 |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
|  | Stage 1: Triage Agent     |   | Stage 3: Vector RAG       |   | Stage 5: Root Cause Agent   |  |
|  | - Signal-based rules      |   | - 384-dim dense retrieval |   | - 4-Tier Fact Attribution   |  |
|  | - Dynamic confidence      |   | - 0.45 Cutoff Guardrail   |   | - Historical Evidence Anchor|  |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
|  | Stage 2: Log Analysis     |   | Stage 4: Duplicate Agent  |   | Stage 6: Remediation Agent  |  |
|  | - Deterministic regex/AST |   | - Cosine Vector Search    |   | - Prescriptive Code Patches |  |
|  | - Failure Frame Analysis  |   | - Threshold Classification|   | - Verification Test Guards  |  |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+------------------------------------------------+--------------------------------------------------+
|                              Data & Vector Storage Layer                                          |
|                                                                                                   |
|  +-----------------------------------------+   +-----------------------------------------------+  |
|  | Relational Storage (SQLAlchemy ORM)     |   | Persistent Vector Store (NumPy / Cosine Index)|  |
|  | - bug_submissions                       |   | - rag/vector_index.pkl (Versioned metadata)   |  |
|  | - historical_defects (Mozilla, Apache,  |   | - 384-dimensional Normalized Dense Vectors   |  |
|  |   Eclipse)                              |   | - Historical Defect Chunks                    |  |
|  | - analysis_results                      |   | - Single Central Similarity Policy            |  |
|  | - knowledge_base_entries (Verified)     |   | - Anti-Hallucination Null Match Guardrail     |  |
|  +-----------------------------------------+   +-----------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Submission-to-Resolution Data Flow

1. **Ingestion & Validation:** Input text, stack traces, logs, or files (`.txt`, `.log`, `.md`, `.json`, max 5MB) are sanitized to eliminate null bytes and control sequences. Uploaded files are strictly parsed as text streams and never executed.
2. **Canonical Identifiers:** Each submission receives a unique UUIDv4 identifier and an ISO-8601 UTC timestamp (`datetime.now(timezone.utc)`).
3. **Stage 1 (Triage) & Stage 2 (Log Analysis):** Run concurrently via `asyncio.gather`.
   - **Triage:** Deterministic keyword signal matching assigns severity (`Critical`, `High`, `Medium`, `Low`), priority (`High`, `Medium`, `Low`), and component category.
   - **Log Parser:** Deterministic regex parsing extracts exception class, failure point (`file:line`), and affected code path without hallucination.
4. **Canonical `BugAnalysisContext` Assembly:** Merges submission, triage, and log analysis into an immutable Pydantic v2 model passed as the single source of truth through all downstream stages.
5. **Stage 3 (RAG Retrieval) & Stage 4 (Duplicate Detection):**
   - The query is embedded into a 384-dimensional vector using `sentence-transformers/all-MiniLM-L6-v2`.
   - The vector store computes cosine similarities against indexed historical defect chunks in `rag/vector_index.pkl`.
   - Centralized similarity thresholds classify candidate matches ($\ge 0.82$ Likely Duplicate, $0.65 - 0.81$ Related Issue, $0.45 - 0.64$ Weak Match, $< 0.45$ Insufficient Historical Evidence).
6. **Stage 5 (Root Cause Analysis):** Synthesizes observed facts with retrieved historical evidence using Four-Tier Fact Attribution (Observed Facts, Historical Evidence, AI Inference, Fix Recommendation). Uses deterministic heuristic synthesis by default, or local Ollama LLM if configured.
7. **Stage 6 (Remediation):** Generates concrete code patch diffs, configuration guidance, and unit/concurrency test recommendations.
8. **Persistence & Live Analytics:** Findings are saved to relational tables. Real-time metrics dynamically recalculate distributions with mathematical population reconciliation.

---

## 3. Technology Choices & Justification

- **FastAPI (Python 3.12):** Native `asyncio` for non-blocking concurrent agent execution and Pydantic v2 runtime validation.
- **Relational Storage:** SQLAlchemy 2.0 with asynchronous SQLite (`aiosqlite`) for zero-dependency local runs and CI suites.
- **Vector Storage (Prototype Implementation):** For the evaluation prototype, historical defect embeddings are stored in a persistent local vector index (`rag/vector_index.pkl`) and compared using cosine similarity via NumPy. This keeps the project fully local, reproducible, and cost-free while maintaining a clean architectural interface for future migration to `pgvector` or Qdrant for larger enterprise deployments.
- **Dense Embedding Encoder:** `sentence-transformers/all-MiniLM-L6-v2` produces dense 384-dimensional normalized vector representations ensuring fast dot-product cosine similarity locally on CPU.
- **Dual Reasoning Mode:** Deterministic heuristic engine for offline reproducibility and automated CI; optional local Ollama LLM (`llama3:8b`) for open-weight neural synthesis without paid cloud APIs.
- **React 18 + Vite + Tailwind CSS + Recharts:** Lightweight, modern developer interface with responsive real-time data visualization.
