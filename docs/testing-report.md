# Automated Testing & Benchmark Report

**Execution Command**: `python -m pytest tests -v`  
**Execution Timestamp**: 2026-10-05 02:10:00 UTC  
**Platform**: Windows (Python 3.12.5, pytest 9.1.1, pluggy 1.6.0)  
**Overall Result**: **25 passed, 0 failed in 15.6s (100% Pass Rate)**

---

## 1. Test Suite Summary Table

| Test Suite File | Category | Tests Executed | Passed | Failed |
| :--- | :--- | :--- | :--- | :--- |
| `tests/unit/test_submission_service.py` | Unit (Security & Sanitization) | 5 | 5 | 0 |
| `tests/unit/test_log_parser.py` | Unit (Deterministic Parsing) | 5 | 5 | 0 |
| `tests/unit/test_rag_pipeline.py` | Unit (Embedder & Vector Store) | 5 | 5 | 0 |
| `tests/unit/test_agents.py` | Unit (Agent Logic & Gating) | 4 | 4 | 0 |
| `tests/unit/test_analytics_reconciliation.py` | Unit (Population Accounting) | 1 | 1 | 0 |
| `tests/integration/test_orchestrator_integration.py` | Integration (Multi-Agent DAG) | 1 | 1 | 0 |
| `tests/integration/test_api_endpoints.py` | Integration (FastAPI REST APIs) | 4 | 4 | 0 |
| **Total Test Suite** | **Comprehensive** | **25** | **25** | **0** |

---

## 2. Five Required Demonstration Scenarios Execution Audit

All 5 mandatory synthetic failure scenarios were executed end-to-end through the complete multi-agent DAG via `scripts/run_demo_scenarios.py`:

| Scenario ID | Name & Failure Mode | Ingested As | Diagnosed Severity | Duplicate? | Top Precedent | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DEMO-01` | NullPointerException Dereference | Stack Trace | High | False (Novel) | Insufficient Evidence | **PASS** |
| `DEMO-02` | Database Connection Pool Deadlock | Error Log | Critical | False (Novel) | Insufficient Evidence | **PASS** |
| `DEMO-03` | JWT Bearer Token Expiration | Error Log | Medium | False (Novel) | Insufficient Evidence | **PASS** |
| `DEMO-04` | Socket Timeout on High Latency | Stack Trace | High | False (Weak) | HTTPCLIENT-2099 (54.7%) | **PASS** |
| `DEMO-05` | OutOfMemory Heap Exhaustion | Error Log | High | False (Weak) | CASSANDRA-2189 (49.5%) | **PASS** |

---

## 3. Pipeline Latency Breakdown
Measured with local `sentence-transformers/all-MiniLM-L6-v2` dense embedding execution across 6 sequential DAG stages:
- **Triage Agent**: 0.2 &ndash; 0.5 ms
- **Log Analysis Agent**: 0.2 &ndash; 0.4 ms
- **RAG Vector Search**: 5.0 &ndash; 12.0 ms (transformer inference on CPU)
- **Duplicate Detection Agent**: 0.1 &ndash; 0.2 ms
- **Root Cause Agent**: 0.4 &ndash; 0.8 ms
- **Remediation Agent**: 0.3 &ndash; 0.6 ms
- **Total In-Memory DAG Latency**: **11.5 &ndash; 14.8 ms per full diagnosis**
