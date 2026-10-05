# Technical Viva Preparation & Comprehensive FAQ

## Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance
**Organization:** Infosys Internship Evaluation Project  
**Author:** Software Architect & QA Lead  
**Evaluation:** Infosys Internship Technical Viva & Defense  

---

### 1. Why RAG?
Software defects in production environments frequently exhibit patterns already diagnosed and resolved in major open-source systems (e.g. Apache Kafka consumer rebalances, Mozilla channel deadlocks, Eclipse UI thread contention). Standard language models or rule-based heuristics cannot memorize every historical defect and tend to hallucinate non-existent issues. RAG grounds the diagnostic pipeline in verifiable historical precedents: the system retrieves actual historical records from public bug trackers (Mozilla Bugzilla, Apache Jira, Eclipse Bugzilla) and supplies them as factual anchors for root cause analysis and remediation.

---

### 2. Why Sentence Transformers?
Lexical search methods (such as BM25 or keyword grep) fail when developers describe the same failure using different vocabulary (e.g., `"connection pool exhausted"` versus `"socket read timeout in HikariCP"`). Sentence Transformers map natural language sentences and stack traces into continuous dense vector representations where semantically equivalent concepts are placed in close geometric proximity, capturing underlying failure mechanisms rather than literal word matches.

---

### 3. Why `all-MiniLM-L6-v2`?
`all-MiniLM-L6-v2` is an open-source distilled transformer model optimized for semantic text similarity. It achieves an optimal trade-off for local edge execution:
- High semantic clustering quality comparable to much larger models.
- Fast local inference on standard consumer CPUs (~5-15 ms per embedding).
- Compact memory footprint (~80 MB model file), eliminating the need for expensive GPU infrastructure or external API services.

---

### 4. Why 384 dimensions?
The `all-MiniLM-L6-v2` model natively projects input text into a 384-dimensional dense vector space ($\mathbb{R}^{384}$). This dimensionality provides sufficient mathematical expressive power to capture fine-grained technical semantics while keeping distance computation (dot product) fast and memory consumption low (approx 1.5 KB per vector).

---

### 5. Why cosine similarity?
Cosine similarity measures the angular orientation between two normalized vectors:
$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
Because all embeddings produced by our pipeline are L2-normalized ($\|\mathbf{u}\|_2 = 1.0$), cosine similarity simplifies directly to the Euclidean dot product ($\mathbf{u} \cdot \mathbf{v}$). This measures semantic direction regardless of text length, preventing longer error logs from artificially dominating shorter stack traces.

---

### 6. How does duplicate detection work?
1. The incoming bug report (title and content) is embedded into a 384-dimensional vector via `all-MiniLM-L6-v2`.
2. The vector store computes cosine similarities against all indexed historical defect chunks in `rag/vector_index.pkl`.
3. The top candidates are ranked and evaluated against the centralized similarity policy:
   - **Score $\ge 0.82$**: Flagged as **Likely Duplicate** with provenance issue link and prior resolution summary.
   - **Score $0.65 - 0.81$**: Classified as **Related Issue** (contextual reference).
   - **Score $0.45 - 0.64$**: Classified as **Weak Match**.
   - **Score $< 0.45$**: Classified as **Insufficient Historical Evidence** (novel issue).

---

### 7. What happens when no historical evidence exists?
If the maximum cosine similarity to any historical record is below the evidence threshold ($0.45$), the retrieval engine returns an empty evidence list. Downstream agents are strictly forbidden from fabricating citations: the Root Cause Agent explicitly outputs `"Insufficient historical evidence found"`, and the Remediation Agent falls back to standard language engineering best practices without claiming historical precedent.

---

### 8. How does the system prevent hallucinated historical evidence?
The anti-hallucination guardrail operates on three levels:
1. **Mathematical Evidence Cutoff:** Queries scoring $< 0.45$ yield an explicit negative message rather than weak false positives.
2. **Four-Tier Epistemic Attribution:** Diagnostic findings strictly distinguish *Observed Facts* (extracted directly from user input), *Historical Evidence* (retrieved from verified KB), *AI Inference* (hypothetical deduction), and *Fix Recommendations*.
3. **No Fabricated Provenance:** Historical records cite genuine public issue IDs (e.g. `KAFKA-10134`, `MOZ-12870`) and verified upstream URLs.

---

### 9. Is this an LLM system?
The platform architecture provides a modular provider interface, but **its core default implementation is a Deterministic Heuristic Engine**, paired with dense semantic embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and deterministic AST/regex parsers. It does **not** rely on paid cloud LLMs (such as OpenAI or Google Gemini). An optional local LLM integration via Ollama (`llama3:8b`) is supported when configured, but the primary system is intentionally deterministic and reproducible offline.

---

### 10. What happens without an LLM?
The system executes completely through its deterministic engines:
- Triage: Keyword and impact rule-based classification.
- Log Analysis: Deterministic AST and regex extraction of exception types, line numbers, and stack frames.
- RAG & Duplicate Detection: Local mathematical vector embedding and cosine ranking.
- Root Cause & Remediation: Pattern-driven causal synthesis and idiomatic patch generation.
This ensures zero downtime, zero network latency to third parties, 100% test reproducibility, and zero API costs.

---

### 11. Why use a local vector index?
For an evaluation prototype and hermetic CI pipelines, storing embeddings in a local binary file (`rag/vector_index.pkl`) and performing vector comparison in-memory via NumPy avoids external daemon dependencies, complex network configurations, and database container requirements. The index can be recreated from scratch in seconds via `python scripts/ingest_historical_data.py`.

---

### 12. Why not pgvector for the prototype?
`pgvector` requires running a dedicated PostgreSQL service with C-level extension binaries, which complicates automated evaluation across disparate operating systems and headless CI runners. Using a local NumPy vector engine provides identical mathematical results (exact cosine similarity) without external infrastructure overhead, while maintaining a clean repository structure and identical mathematical behavior.

---

### 13. How does the system scale?
- **Read Scalability:** The FastAPI backend is asynchronous (`asyncio`), handling high-concurrency non-blocking I/O.
- **Vector Index Scalability:** While the prototype uses an in-memory NumPy matrix for 15-10,000 records, the `VectorStore` interface is cleanly decoupled, allowing drop-in migration to PostgreSQL with `pgvector`, Qdrant, or Milvus for million-scale enterprise defect databases.
- **Horizontal Scaling:** Stateless API instances can sit behind an NGINX load balancer.

---

### 14. How are historical defects verified?
Every active record in the historical knowledge base is validated via `scripts/validate_historical_data.py`:
- Real public issue IDs from Mozilla Bugzilla, Apache Jira, or Eclipse Bugzilla.
- Valid live upstream HTTP/HTTPS issue tracker URLs.
- Authentic titles, descriptions, and component assignments matching upstream records.
- Verified status flag (`verified: true`) and explicit data type (`data_type: "historical"`).
Records that cannot be genuinely verified against public bug trackers are excluded from the active KB.

---

### 15. What are the limitations?
1. **Curated KB Size:** The prototype knowledge base contains 15 curated public defects; real enterprise deployments require continuous synchronization with active bug trackers.
2. **Deterministic Fallback Scope:** In offline mode without Ollama, causal hypotheses are drawn from deterministic heuristic templates rather than open-ended neural generation.
3. **Log Obfuscation:** The log parser requires unminified stack traces; minified client JavaScript or obfuscated Android bytecode requires source-map / ProGuard de-obfuscation.
4. **Duplicate Recall:** Under high semantic thresholding ($\ge 0.82$), duplicate precision is 100%, but recall is 60% on edge cases with divergent phrasing.

---

### 16. How were evaluation metrics calculated?
Evaluation metrics are dynamically computed by executing `scripts/evaluate_agents.py` against 10 ground-truth test cases in `data/validation_dataset.json`. The script compares agent predictions against actual labels to compute:
- **Severity Accuracy:** Correct Severity / Total Cases = 80.0% (8/10)
- **Priority Accuracy:** Correct Priority / Total Cases = 80.0% (8/10)
- **Duplicate Accuracy:** (TP + TN) / Total Cases = 80.0% (8/10)
- **Duplicate Precision:** TP / (TP + FP) = 3 / (3 + 0) = 100.0%
- **Duplicate Recall:** TP / (TP + FN) = 3 / (3 + 2) = 60.0%
- **Duplicate F1-Score:** Harmonic mean = 75.0%
No numbers are hardcoded; metrics are recorded in `reports/latest_evaluation.json`.

---

### 17. Why is duplicate recall lower than precision?
In enterprise software defect tracking, false duplicates are catastrophic: incorrectly merging a novel defect into an existing issue causes the new bug to be ignored and shipped to production. Therefore, our centralized similarity policy deliberately prioritizes **high precision** (100% in empirical benchmarks) with a strict cutoff ($\ge 0.82$). Borderline cases ($0.65 - 0.81$) are flagged as *Related Issues* rather than duplicates, resulting in 60% recall with zero false duplicate alarms.

---

### 18. How does KB growth work?
To prevent memory pollution from unverified AI hypotheses, automated diagnoses do **not** automatically enter the knowledge base. Only **human-verified bugs** are promoted:
1. Candidate defect is submitted and diagnosed.
2. An engineer investigates and verifies the resolution in the UI.
3. Upon approval, the confirmed root cause and resolution are serialized, embedded via `all-MiniLM-L6-v2`, and indexed into the active vector store.

---

### 19. Why are the five demos synthetic?
The five demonstration scenarios (`DEMO-01` through `DEMO-05`) are explicitly synthetic test fixtures designed to stress-test the end-to-end pipeline across five archetypal software engineering failure modes (NullPointer, DB Connection Deadlock, JWT Expiration, Network Socket Timeout, JVM OutOfMemory). They are transparently marked with `data_type: "synthetic"` and `synthetic_demo: true` to prevent any confusion with historical defect records.

---

### 20. How would you productionize the system?
1. **Infrastructure:** Deploy the FastAPI backend on Kubernetes with horizontal pod autoscaling and migrate the vector index to PostgreSQL with `pgvector` or Qdrant.
2. **Integrations:** Add bi-directional webhooks for GitHub Issues, Jira, and Slack alerting.
3. **CI/CD Integration:** Automatically ingest CI test failure logs and suggest pull request fixes via GitHub Actions bots.
4. **Authentication:** Implement enterprise OAuth2 / OpenID Connect and Role-Based Access Control (RBAC).
5. **Observability:** Instrument OpenTelemetry distributed tracing and Prometheus/Grafana metrics dashboards for pipeline latency monitoring.
