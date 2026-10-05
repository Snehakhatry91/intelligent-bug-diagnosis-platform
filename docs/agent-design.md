# Multi-Agent Architecture & Orchestration Specification

## Intelligent Bug Diagnosis Platform
**Organization:** Infosys Internship Evaluation Project  
**Author:** AI/ML & Software Architect  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. Multi-Agent Design Philosophy

Defect diagnosis requires distinct technical competencies that cannot be reliably performed by a single monolithic prompt:
- Stack trace parsing requires **deterministic syntactic extraction** (regex and AST pattern recognition).
- Triage classification requires **domain impact modeling** and rule-based heuristic scoring.
- Duplicate detection requires **dense vector geometry** using local SentenceTransformer embeddings and cosine similarity.
- Root cause deduction requires **abductive reasoning grounded in empirical facts** and retrieved historical evidence.
- Remediation requires **prescriptive code engineering** with concrete patch diffs and automated test specifications.

Decomposing the problem into specialized agents enables modular unit testing, isolated confidence calculation, predictable offline execution, and graceful degradation under partial failures.

---

## 2. Orchestration Architecture & Workflow

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

---

## 3. Detailed Agent Specifications

### 3.1 Triage Agent
- **Role:** Assesses defect severity, priority, and subsystem category from submitted text and error logs.
- **Input:** Title, raw content, and submission metadata.
- **Processing:** Rule-based heuristic pattern matching across crash indicators (e.g. fatal signals, data corruption, connection saturation), subsystem keyword clustering, and business impact rules.
- **Output:**
  - `severity`: `Critical`, `High`, `Medium`, or `Low`.
  - `priority`: `High`, `Medium`, or `Low`.
  - `affected_component`: Detected subsystem (e.g., `Authentication / Security`, `Database / Persistence`, `Memory & Runtime`, `Network / Transport`, `Core / Concurrency`).
  - `confidence_score`: Dynamic normalized float ($0.50 - 0.96$) derived from matched signal density.
  - `reasoning`: Technical justification detailing which keywords and failure indicators triggered the classification.
- **Evidence:** Explicitly cites keyword matches, exception patterns, and impact triggers found in the report.
- **Confidence Derivation:** Base confidence (0.50) + keyword signal weight (up to 0.30) + stack trace presence (0.10) + component match clarity (0.06).
- **Limitations:** Cannot infer semantic business priority for novel proprietary terminology without explicit keywords.

### 3.2 Log Analysis Agent
- **Role:** Performs deterministic structural parsing of stack traces and crash logs.
- **Input:** Multi-line log text, stack trace, or error output.
- **Processing:** Deterministic regex parsing supporting Java stack traces (`at package.Class.method(Class.java:123)`), Python tracebacks (`File "...", line ...`), Node.js/JavaScript traces, Go panics, and POSIX system crash signals (`SIGSEGV`, `DeadlockDetected`).
- **Output:**
  - `exception_type`: Standardized exception class.
  - `error_message`: Core error description extracted from the log.
  - `failure_point`: File and line number (`file:line`).
  - `affected_code_path`: Qualified package/method path.
  - `key_signals`: List of critical diagnostic tokens.
  - `confidence_score`: Structural completeness score ($0.60 - 0.98$).
- **Evidence:** Directly quotes extracted lines from the provided stack trace.
- **Strict Rule:** If a frame is missing from the input, the agent explicitly returns `"Information unavailable in submitted text"` rather than hallucinating placeholder source files.
- **Limitations:** Requires unminified stack traces; minified JavaScript bundles or obfuscated bytecode require source maps.

### 3.3 Duplicate Detection Agent
- **Role:** Detects duplicate and related defects against historical records using semantic vector similarity.
- **Input:** Submission title, content, canonical context, and candidate embeddings.
- **Processing:** Embeds the incoming report using `sentence-transformers/all-MiniLM-L6-v2`, computes cosine similarities against indexed historical defect vectors in `rag/vector_index.pkl`, and applies the centralized similarity policy.
- **Output:**
  - `is_duplicate`: Boolean flag ($\text{similarity} \ge 0.82$).
  - `classification`: `Likely Duplicate` ($\ge 0.82$), `Related Issue` ($0.65 - 0.81$), `Weak Match` ($0.45 - 0.64$), or `Insufficient Historical Evidence` ($< 0.45$).
  - `similarity_score`: Cosine similarity of the top historical match.
  - `top_match_id`: Provenance issue ID of top match (e.g., `MOZ-12870`, `KAFKA-10134`).
  - `matches`: Ranked candidate matches with provenance links and resolution summaries.
- **Evidence:** Exact cosine similarity scores and public bug tracker URLs.
- **Confidence Derivation:** Directly proportional to cosine similarity score.
- **Limitations:** Precision and recall depend on the breadth and depth of the indexed historical corpus.

### 3.4 Root Cause Agent
- **Role:** Formulates a causal diagnosis combining observed crash facts with retrieved historical precedents.
- **Input:** Canonical `BugAnalysisContext` + retrieved RAG evidence items.
- **Processing:** Four-Tier Attribution reasoning synthesized via the deterministic reasoning engine or local Ollama LLM.
- **Output:**
  - `hypothesis`: Abductive explanation of the failure mechanism.
  - `observed_facts`: Concrete empirical facts verified directly from user input.
  - `historical_evidence`: Corroborating precedent issues retrieved via RAG above the 0.45 threshold.
  - `ai_inference`: Deductive reasoning connecting observed facts to the hypothesis.
  - `confidence_score`: Evidence-backed confidence score ($0.50 - 0.95$).
- **Evidence Policy:** If RAG retrieves 0 matches above 0.45, historical evidence explicitly states `"Insufficient historical evidence found"`. The agent never invents citations.
- **Confidence Derivation:** Grounded in signal density: High when deterministic log evidence and historical precedent align; moderate when relying on heuristic inference alone.
- **Limitations:** In offline mode without Ollama, causal hypotheses are drawn from deterministic heuristic templates.

### 3.5 Remediation Agent
- **Role:** Generates prescriptive engineering solutions, code patches, and test recommendations.
- **Input:** `BugAnalysisContext` + root cause hypothesis + historical fix evidence.
- **Processing:** Synthesizes actionable engineering recommendations, concrete patch diffs, and verification test specifications based on known architectural best practices and verified historical resolutions.
- **Output:**
  - `summary`: High-level actionable fix strategy.
  - `technical_explanation`: Detailed mechanism explaining why the fix resolves the root cause.
  - `affected_file`: Target code file or configuration identified for modification.
  - `patch_diff`: Unified diff snippet containing concrete defensive guards or configuration updates.
  - `recommended_tests`: Structured list of verification test cases (unit, integration, concurrency) with descriptions.
- **Evidence:** References retrieved historical fix summaries when available, or standard language idioms (e.g. defensive null checks, bounded thread pools).
- **Limitations:** Generates targeted defensive guards and idiomatic patches; full architectural rewrites require human software engineers.

---

## 4. LLM Provider Abstraction & Reasoning Engine

The platform implements a transparent, dual-mode reasoning architecture:

```
                           +------------------------+
                           |   get_llm_provider()   |
                           +-----------+------------+
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
+-----------------------------------+     +----------------------------------------+
| Deterministic Heuristic Engine    |     | Ollama Local LLM Provider              |
| (Default / Fallback)              |     | (Optional Local Inference)             |
| - 100% offline & zero cost        |     | - Configured via LLM_PROVIDER="ollama" |
| - Reproducible benchmark scores   |     | - Connects to local http://localhost:11434|
| - Deterministic pattern synthesis |     | - Uses open weights (llama3:8b)        |
+-----------------------------------+     +----------------------------------------+
```

1. **`DeterministicHeuristicEngine` (Default Engine):**
   - Serves as the primary engine for evaluation, CI pipelines, and hermetic offline testing.
   - Transparently uses structural pattern-matching and deterministic heuristic templates.
   - **Critical Fact:** This engine is explicitly labeled as deterministic rules and does not simulate or pretend to be an LLM.

2. **`OllamaProvider` (Optional Local LLM Integration):**
   - Connects to a locally running Ollama instance (`http://localhost:11434`) using open-weight models (e.g., `llama3:8b`).
   - Activated by setting `LLM_PROVIDER=ollama` in environment or configuration.
   - Fully open-source, local, and private with zero cloud API keys required.

3. **External API Policy:**
   - The platform core is strictly free, open-source, and locally runnable. It does not include or depend on paid external cloud APIs (such as OpenAI or Google Gemini).
