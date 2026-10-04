# Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3-purple.svg)](https://vite.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4.0-cyan.svg)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Pytest-25%2F25%20Passed-emerald.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous multi-agent software engineering platform that accelerates defect triage, decompiles stack traces deterministically, searches historical defect corpora (Mozilla, Apache, Eclipse) via 384-dimensional dense semantic vector similarity, identifies duplicates, formulates anti-hallucinated root cause hypotheses, and produces production-grade code patches with automated test plans.

**Organization**: Infosys Internship Evaluation Project  
**Copyright**: Copyright (c) 2025 Vidzai Digital. MIT License.

---

## 🏛️ System Architecture

```
Bug Submission (Text, Stack Trace, or 5MB File Upload)
                     │
                     ▼
             [Triage Agent]
         (Severity, Priority, Component)
                     │
                     ▼
          [Log Analysis Agent]
   (Deterministic Java, Python, Node, Go)
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
   (Actionable Patches & Test Suites)
                     │
                     ▼
        [Canonical Findings UI]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 [Defect Analytics]    [Verified KB Growth]
  (Reconciled &sum;=N)    (Human Verification)
```

---

## 🚀 Quick Start Guide

### 1. Ingest Data & Initialize Vector Index
```bash
python scripts/ingest_historical_data.py
```

### 2. Start Backend API (FastAPI)
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 3. Start Frontend Dashboard (React 18 + Vite)
```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Testing & Evaluation

### Run Automated Pytest Suite
```bash
python -m pytest tests -v
```
**Result: 25 passed in 0.97s (100% Pass Rate)**

### Run 5 Required Demonstration Scenarios
```bash
python scripts/run_demo_scenarios.py
```
Executes the five mandatory failure modes end-to-end:
1. `NullPointerException` (High Severity, False Duplicate)
2. `Database Connection Pool Deadlock` (Critical Severity, Related Issue)
3. `JWT Bearer Auth Token Expiration` (Medium Severity, **Likely Duplicate &ge; 0.82**)
4. `Network Socket Timeout on External API` (High Severity, False Duplicate)
5. `OutOfMemory Heap Space Exhaustion` (High Severity, **Likely Duplicate &ge; 0.82**)

### Run Empirical Validation Benchmark
```bash
python scripts/evaluate_agents.py
```
- Triage Severity Accuracy: **90.0%**
- Triage Priority Accuracy: **80.0%**
- Duplicate Detection Accuracy: **90.0%**
- Duplicate Detection Precision: **100.0%** (Zero false duplicates)
- Duplicate Detection Recall: **80.0%**
- Duplicate Detection F1-Score: **88.9%**

---

## 📋 Infosys Agile & Technical Artifacts

- [Product Backlog (MOSCOW)](PRODUCT_BACKLOG.md)
- [Sprint Backlog (0.5 to 12h tasks)](SPRINT_BACKLOG.md)
- [Daily Stand-up Meeting Log](STANDUP_MEETINGS.md)
- [Sprint Retrospectives](RETROSPECTIONS.md)
- [Internal Defect Tracker](DEFECT_TRACKER.md)
- [Executed Unit Test Plan (25/25 Passed)](UNIT_TEST_PLAN.md)
- [Final Completion Checklist (34/34 Pass)](PROJECT_COMPLETION_CHECKLIST.md)
- [Final Status Report](FINAL_STATUS.md)

### Technical Documentation
- [System Architecture](docs/architecture.md)
- [Agent Design & DAG](docs/agent-design.md)
- [RAG & Vector Policy](docs/rag-design.md)
- [Canonical Data Models](docs/data-model.md)
- [API REST Documentation](docs/api-documentation.md)
- [Local Setup Guide](docs/setup-guide.md)
- [Production Deployment Guide](docs/deployment-guide.md)
- [Automated Testing Report](docs/testing-report.md)
- [Empirical Evaluation Report](docs/evaluation-report.md)
- [Platform User Guide](docs/user-guide.md)
- [Project Final Report](docs/project-report.md)
- [Evaluation Demonstration Walkthrough](docs/demo-guide.md)
- [Comprehensive Technical FAQ (23 Interview Questions)](docs/faq.md)

---

## 🔒 Security & Anti-Hallucination Guarantees
- 5 MB maximum file upload ceiling
- Allowed extensions strictly enforced (`.txt`, `.log`, `.md`, `.json`)
- Null-byte and control-character sanitization
- Zero uploaded-file execution guarantee (parsed purely as text)
- Four-Tier Epistemic Attribution separating empirical facts from AI inferences
- Strict population reconciliation ($\sum Counts \equiv Total Submissions$)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  
Copyright (c) 2025 Vidzai Digital.
