# Multi-Agent Architecture & Orchestration Specification

## Intelligent Bug Diagnosis Platform
**Organization:** Infosys Internship Evaluation Project  
**Author:** AI/ML & Software Architect  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. Multi-Agent Design Philosophy

Defect diagnosis requires distinct technical competencies that cannot be reliably performed by a single monolithic prompt:
- Stack trace parsing requires **deterministic syntactic extraction**.
- Triage classification requires **domain impact modeling**.
- Duplicate detection requires **dense vector geometry**.
- Root cause deduction requires **abductive reasoning grounded in empirical facts**.
- Remediation requires **prescriptive code engineering**.

Decomposing the problem into specialized agents enables modular unit testing, isolated confidence calculation, and graceful degradation.

---

## 2. Agent Responsibilities & Contracts

```
                                  [Bug Submission]
                                          │
                                          ├─────────────────────────┐
                                          ▼                         ▼
                                 +------------------+     +--------------------+
                                 |   Triage Agent   |     | Log Analysis Agent |
                                 +--------+---------+     +---------+----------+
                                          │                         │
                                          └───────────┬─────────────┘
                                                      │
                                                      ▼
                                         [BugAnalysisContext Model]
                                                      │
                                                      ├─────────────────────────┐
                                                      ▼                         ▼
                                             +------------------+     +--------------------+
                                             |   RAG Engine     |     |  Duplicate Agent   |
                                             +--------+---------+     +---------+----------+
                                                      │                         │
                                                      └───────────┬─────────────┘
                                                                  │
                                                                  ▼
                                                      +-----------------------+
                                                      |   Root Cause Agent    |
                                                      +-----------+-----------+
                                                                  │
                                                                  ▼
                                                      +-----------------------+
                                                      |   Remediation Agent   |
                                                      +-----------+-----------+
                                                                  │
                                                                  ▼
                                                      [Structured Findings]
```

### 2.1 Triage Agent
- **Input:** Title, raw content, and submission context.
- **Output:**
  - `severity`: `Critical`, `High`, `Medium`, `Low`.
  - `priority`: `High`, `Medium`, `Low`.
  - `affected_component`: Detected subsystem (e.g. `Authentication / Security`, `Database / Storage`, `Core / Memory Management`, `Messaging / Distributed`, `Network / HTTP`).
  - `confidence_score`: Normalized float derived empirically from detected signals ($0.50 - 0.96$).
  - `reasoning`: Technical justification.

### 2.2 Log Analysis Agent
- **Input:** Multi-line log text or stack trace.
- **Output:**
  - `exception_type`: Specific exception class (e.g. `java.lang.NullPointerException`, `psycopg2.errors.DeadlockDetected`, `KeyError`).
  - `error_message`: Primary error message.
  - `failure_point`: Exact file and line number (`file:line`).
  - `affected_code_path`: Qualified package/method path.
  - `key_signals`: Array of critical diagnostic signals.
  - `confidence_score`: Completeness score based on located tokens.
  - *Strict Rule:* If information is unavailable, explicitly returns `"Information unavailable"` with explanation.

### 2.3 Duplicate Detection Agent
- **Input:** Submission title, content, and canonical context.
- **Output:**
  - `classification`: `likely duplicate`, `related issue`, `weak match`, or `no meaningful match`.
  - `top_similarity_score`: Cosine similarity score of top hit.
  - `matches`: Ranked candidate defects with historical resolutions.

### 2.4 Root Cause Agent
- **Input:** `BugAnalysisContext` + retrieved RAG evidence.
- **Output:**
  - `hypothesis`: Abductive explanation of failure mechanism.
  - `confidence_score`: Confidence score.
  - `observed_facts`: Facts extracted from user submission.
  - `historical_evidence`: Corroborating historical defects from RAG.
  - `ai_inference`: Deductive logic connecting facts to evidence.

### 2.5 Remediation Agent
- **Input:** `BugAnalysisContext` + validated root cause hypothesis.
- **Output:**
  - `recommendations`: Actionable steps including `action`, `affected_area`, `implementation_guidance` (code snippet), `supporting_evidence`, and `confidence`.

---

## 3. LLM Provider Abstraction & Fallback Engine

The platform provides a pluggable LLM interface supporting:
1. `OllamaLLM`: Local open-weight models (`llama3:8b`).
2. `OpenAILLM`: OpenAI API when `OPENAI_API_KEY` is configured.
3. `GeminiLLM`: Google Gemini API when `GEMINI_API_KEY` is configured.
4. `DeterministicHeuristicEngine`: Transparently labeled fallback engine providing deterministic regex and rule evaluations for offline CI and automated testing.
