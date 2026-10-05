# PROJECT IMPLEMENTATION PLAN (FULL REBUILD)
## Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance
**Organization:** Infosys Internship Evaluation Project  
**Author / Lead:** Software Architect, AI/ML & DevOps Engineer  
**Date:** October 2026  
**License:** MIT License — Copyright (c) 2025 Vidzai Digital  

---

## 1. Executive Summary & Core Requirements

This document establishes the ground-up architectural specification and milestone delivery plan for the **Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance**.

The system addresses the four major bottlenecks in modern defect resolution:
1. **Prolonged Triage Latency:** Manual inspection of complex multi-tier stack traces and server crash logs.
2. **Defect Duplication:** Redundant defect filings that overwhelm issue backlogs.
3. **Tribal Knowledge Silos:** Inability to retrieve past resolved defects and proven code patches when identical failures recur.
4. **LLM Hallucinations:** Unconstrained generative models fabricating non-existent library methods and invalid commit IDs.

### Primary Operational Mandates
- **End-to-End Real Execution:** Zero mock simulations, zero hard-coded AI results, zero synthetic accuracy metrics, zero fake vector retrieval.
- **Strict Data Consistency:** Every analytics metric must mathematically reconcile with its target population (e.g. $\sum \text{Severity Counts} = \text{Total Submitted Defects}$).
- **Single Global Vector Similarity Policy:** Centralized threshold definition:
  - $\ge 0.82$: `likely duplicate`
  - $0.65 - 0.81$: `related issue`
  - $0.45 - 0.64$: `weak match`
  - $< 0.45$: `no meaningful match` & `"Insufficient historical evidence found"`
- **Strict 4-Tier Attribution:** Clear separation of `OBSERVED FACT`, `HISTORICAL EVIDENCE`, `AI INFERENCE`, and `FIX RECOMMENDATION`.
- **Zero Deprecation Warnings:** Modern Python 3.12 standards (`datetime.now(timezone.utc)`).

---

## 2. Six Required Core Modules

```
                    +------------------------------------+
                    |    Module 1: Bug Submission        |
                    | (Text, Stack Trace, Log, Files)    |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |    Module 3: Multi-Agent Pipeline  |
                    |  - Stage 1: Triage Agent           |
                    |  - Stage 2: Log Analysis Agent     |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    | Canonical BugAnalysisContext       |
                    +-----------------+------------------+
                                      |
                    +-----------------+------------------+
                    |    Module 2: Historical RAG        |
                    |    Module 4: Duplicate Detection   |
                    | (Mozilla, Apache, Eclipse Corpora) |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |  - Stage 5: Root Cause Agent       |
                    |  - Stage 6: Remediation Agent      |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |    Module 5: Structured Findings   |
                    |   (Enterprise Developer Dashboard) |
                    +-----------------+------------------+
                                      |
                    +-----------------+------------------+
                    |    Module 6: Live Analytics &      |
                    |    Knowledge Base Growth           |
                    +------------------------------------+
```

1. **Module 1: Bug Submission Module:** Ingests direct text, stack traces, logs, and files (`.txt`, `.log`, `.md`, `.json`, max 5MB). Null-byte sanitization, zero-execution security policy, UUIDv4 generation, ISO-8601 UTC timestamping.
2. **Module 2: Historical Defect Knowledge Base & RAG Pipeline:** Authentic defect records from Mozilla Firefox, Apache Software Foundation (Tomcat, Spark, Kafka, Lucene, Cassandra), and Eclipse IDE (JDT, Platform, Equinox, SWT). Domain chunking, 384-dimensional dense semantic vector indexing, cosine similarity.
3. **Module 3: Multi-Agent Orchestration:** Specialized asynchronous DAG agents:
   - *Triage Agent:* Severity, Priority, Subsystem, and empirical confidence score.
   - *Log Analysis Agent:* Deterministic regex/AST grammar parser extracting exception class, failure point, affected method, and key log signals.
   - *Root Cause Agent:* RAG evidence synthesizer maintaining 4-tier attribution.
   - *Duplicate Detection Agent:* 4-tier similarity matching.
   - *Remediation Agent:* Actionable code patches, configuration guidance, and unit test guards.
4. **Module 4: Duplicate Detection & Similarity Matching:** Cosine distance comparison against normalized dense feature vectors with single central policy.
5. **Module 5: Structured Findings & Resolution Display:** Enterprise React 18 + Vite + TypeScript web interface with Tailwind CSS, Lucide icons, and Recharts.
6. **Module 6: Defect Pattern Analytics & Knowledge Base Growth:** Live SQL aggregations guaranteeing population reconciliation and promotion of engineer-verified resolutions into active vector store.

---

## 3. Technology Stack & Technical Justification

| Subsystem | Technology | Architectural Justification |
|---|---|---|
| **Frontend Framework** | **React 18 + Vite + TypeScript** | Sub-second HMR, strict type safety aligned with backend Pydantic models. |
| **Styling & Icons** | **Tailwind CSS v4 + Lucide React** | Enterprise developer aesthetics (dark mode `#0b0f19`, clear status color scales, high density data views). |
| **Visual Analytics** | **Recharts** | Reactive SVG charts bound dynamically to database aggregations. |
| **Backend API** | **Python 3.12 + FastAPI + Pydantic v2** | High-throughput asynchronous endpoints, automatic OpenAPI/Swagger schema documentation. |
| **Relational Database** | **SQLite (Async SQLAlchemy 2.0 + aiosqlite)** | Zero-config local execution and CI testing, with clean migration path to PostgreSQL for production. |
| **Vector Engine** | **Persistent Local Vector Index (rag/vector_index.pkl)** | 384-dimensional normalized dense vectors with NumPy cosine similarity; migration path to pgvector/Qdrant. |
| **Embeddings** | **Sentence Transformers (`all-MiniLM-L6-v2`)** | 384-dimensional L2-normalized dense embeddings running locally on CPU without paid third-party dependencies. |
| **Reasoning Engine** | **Deterministic Heuristic Engine (Default)** | Deterministic rule-based synthesis for hermetic offline testing; optional local Ollama integration (`llama3:8b`). |
| **Testing** | **Pytest + pytest-asyncio + httpx** | Automated unit, integration, and evaluation suites. |

---

## 4. Single Unified Similarity & Anti-Hallucination Policy

All modules and agents strictly adhere to the following centrally configured thresholds:

```python
SIMILARITY_POLICY = {
    "DUPLICATE_THRESHOLD": 0.82,    # Score >= 0.82  -> Likely Duplicate
    "RELATED_THRESHOLD": 0.65,      # 0.65 <= Score < 0.82 -> Related Issue
    "WEAK_THRESHOLD": 0.45,         # 0.45 <= Score < 0.65 -> Weak Match
    "NO_MATCH_THRESHOLD": 0.45      # Score < 0.45   -> No Meaningful Match / Insufficient Evidence
}
```

When no historical defect scores $\ge 0.45$, the RAG engine explicitly outputs:
`"Insufficient historical evidence found."`

---

## 5. Mathematical Population Reconciliation in Analytics

To guarantee complete consistency:
1. **Submitted Defects Population ($N_{\text{sub}}$):** Total user/system submissions stored in `bug_submissions`.
   $$\sum_{s \in \{\text{Critical, High, Medium, Low}\}} \text{Count}(s) = N_{\text{sub}}$$
   $$\sum_{p \in \{\text{High, Medium, Low}\}} \text{Count}(p) = N_{\text{sub}}$$
2. **Historical Corpora Population ($N_{\text{hist}}$):** Reference defects from Mozilla, Apache, and Eclipse stored in `historical_defects`.
3. **Verified Knowledge Base Population ($N_{\text{kb}}$):** Verified resolutions stored in `knowledge_base_entries`.
4. Automated verification assertions ensure that dashboard totals never contradict individual metric distributions.

---

## 6. Milestone Execution Roadmap

- **Milestone 1:** Architecture, data models, Bug Submission Module, Historical Defect Corpora ingestion, and RAG pipeline with unified similarity policy.
- **Milestone 2:** Triage Agent, Log Analysis Agent, Canonical `BugAnalysisContext`, Orchestrator DAG, and empirical validation against ground-truth dataset.
- **Milestone 3:** Root Cause Agent (3-tier attribution), Duplicate Detection Agent, Remediation Agent, and Structured Findings Web Interface.
- **Milestone 4:** Live Defect Pattern Analytics (reconciled totals), Knowledge Base Growth pipeline, 5 Demonstration Scenarios, Infosys Agile Artifacts, Defect Tracker, Unit Test Plan, and Final Audit.
