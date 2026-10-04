# System Architecture & Technical Specification

## Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance
**Organization:** Infosys Internship Evaluation Project  
**Author:** Software Architect & Engineering Lead  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. High-Level Architecture Overview

The Intelligent Bug Diagnosis Platform is structured as an asynchronous micro-architecture combining deterministic AST/regex parsers, an agentic reasoning Directed Acyclic Graph (DAG), and a dense vector Retrieval-Augmented Generation (RAG) knowledge engine grounded in open-source defect repositories from Mozilla, Apache, and Eclipse.

```
+---------------------------------------------------------------------------------------------------+
|                                  Developer / QA User (Web UI)                                     |
|  - Modern Dark Theme (Tailwind CSS v4)                                                            |
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
|  | Stage 1: Triage Agent     |   | Stage 3: Duplicate Agent  |   | Stage 5: Root Cause Agent   |  |
|  | - Severity & Priority     |   | - Cosine Vector Search    |   | - 4-Tier Fact Attribution   |  |
|  | - Component Hotspot       |   | - Threshold Classification|   | - Historical Evidence Anchor|  |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
|  | Stage 2: Log Analysis     |   | Stage 4: Vector RAG       |   | Stage 6: Remediation Agent  |  |
|  | - Exception Extraction    |   | - 384-dim Dense Retrieval |   | - Prescriptive Code Patches |  |
|  | - Failure Frame Analysis  |   | - 0.45 Cutoff Guardrail   |   | - Unit Test Guards          |  |
|  +---------------------------+   +---------------------------+   +-----------------------------+  |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+------------------------------------------------+--------------------------------------------------+
|                              Data & Vector Storage Layer                                          |
|                                                                                                   |
|  +-----------------------------------------+   +-----------------------------------------------+  |
|  | Relational Storage (SQLAlchemy ORM)     |   | Dense Vector Store (Cosine Index / pgvector)  |  |
|  | - bug_submissions                       |   | - 384-dimensional Normalized Vectors          |  |
|  | - historical_defects (Mozilla, Apache,  |   | - Historical Defect Chunks                    |  |
|  |   Eclipse)                              |   | - Cosine Similarity Ranking                   |  |
|  | - analysis_results                      |   | - Single Central Similarity Policy            |  |
|  | - knowledge_base_entries (Verified)     |   | - Anti-Hallucination Null Match Guardrail     |  |
|  +-----------------------------------------+   +-----------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Submission-to-Resolution Data Flow

1. **Ingestion & Validation:** Input text, stack traces, logs, or files (`.txt`, `.log`, `.md`, `.json`, max 5MB) are sanitized to eliminate null bytes and control sequences. Uploaded files are strictly parsed as text streams and never executed.
2. **Canonical Identifiers:** Each submission receives a unique UUIDv4 identifier and an ISO-8601 UTC timestamp (`datetime.now(timezone.utc)`).
3. **Stage 1 (Triage) & Stage 2 (Log Analysis):** Run concurrently via `asyncio.gather`. Triage outputs dynamic severity (`Critical`, `High`, `Medium`, `Low`), priority (`High`, `Medium`, `Low`), and component. Log parser extracts exception class, failure point (`file:line`), and affected code path.
4. **Canonical BugAnalysisContext Assembly:** Merges submission, triage, and log analysis into an immutable Pydantic model.
5. **Stage 3 (RAG Retrieval) & Stage 4 (Duplicate Detection):** Vector engine compares query embedding against indexed defect vectors using the single global similarity policy.
6. **Stage 5 (Root Cause Analysis):** Synthesizes observed facts with retrieved historical evidence, explicitly distinguishing Observed Facts from Historical Evidence and AI Inference.
7. **Stage 6 (Remediation):** Generates concrete code patches, configuration guidance, and unit test guards.
8. **Persistence & Live Analytics:** Findings are saved to relational tables. Real-time metrics dynamically recalculate distributions with mathematical population reconciliation.

---

## 3. Technology Choices & Justification

- **FastAPI (Python 3.12):** Provides native `asyncio` for non-blocking concurrent agent execution and Pydantic v2 runtime validation.
- **Dual-Mode Database Architecture:** Native PostgreSQL + `pgvector` for containerized production and embedded SQLite + numpy vector index for zero-dependency local runs and CI suites.
- **Sentence Transformers / Dense Encoder:** Dense 384-dimensional normalized vector representations ensuring fast dot-product cosine similarity without reliance on paid third-party APIs.
- **React 18 + Vite + Tailwind CSS v4 + Recharts:** Lightweight, modern developer interface with responsive real-time data visualization.
