# Technical Interview Preparation & Comprehensive FAQ

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Evaluation**: Infosys Internship Technical Viva & Defense

---

### 1. What problem does the project solve?
In enterprise software engineering, engineering teams spend up to 40% of their time manually triaging bug reports, analyzing noisy stack traces, identifying duplicate tickets, and searching historical issue trackers for prior fixes. This platform automates the end-to-end defect diagnostic lifecycle: it ingests reports/logs, triages severity and priority, deterministically decompiles stack traces, performs semantic vector retrieval over historical defect repositories, identifies duplicates, formulates anti-hallucinated root causes, and generates drop-in code patches with automated test plans.

---

### 2. Why multi-agent?
Monolithic LLM prompts suffer from context crowding, cognitive drift, hallucinated stack traces, and lack of deterministic validation. A multi-agent architecture decomposes the problem into specialized, single-responsibility agents:
- **Triage Agent**: Specializes in business impact and severity classification.
- **Log Analysis Agent**: Deterministic regex and structural parsing without LLM hallucination.
- **RAG Engine**: Pure mathematical vector similarity search.
- **Duplicate Detection Agent**: Strict threshold-based gating.
- **Root Cause Agent**: Causal synthesis constrained by empirical facts.
- **Remediation Agent**: Code generation and test specification.
This separation of concerns enables independent testing, isolated latency telemetry, and fault tolerance.

---

### 3. Why RAG (Retrieval-Augmented Generation)?
Software defects rarely occur in complete isolation; modern applications frequently encounter errors already diagnosed and resolved in open-source foundations (e.g., Apache Kafka connection pool exhaustion, Mozilla HTTP channel null dereferences, Eclipse UI deadlocks). RAG allows the platform to ground its root cause reasoning and remediation recommendations in authentic, verifiable historical precedents rather than relying on an LLM's static training memory.

---

### 4. What are embeddings?
Embeddings are dense numerical vector representations of text in a continuous multi-dimensional geometric space (384 dimensions in our architecture). Semantic embeddings map words, phrases, and exception signatures such that concepts with similar software engineering meanings reside close to each other in vector space (e.g., `NullPointerException` and `Cannot invoke method on null object` share high cosine similarity).

---

### 5. What is semantic similarity?
Semantic similarity measures how closely two pieces of text align in technical meaning, rather than merely counting lexical keyword overlaps. In defect analysis, two engineers might describe the same crash differently ("PostgreSQL connection refused" vs. "HikariCP worker pool timeout"). Semantic similarity enables the system to detect that both describe database transport saturation.

---

### 6. How does vector search work?
Vector search compares the query vector $\mathbf{u}$ against all indexed document vectors $\mathbf{v}$ using cosine similarity:
$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
Because all vectors in our platform are normalized to unit L2 length ($\|\mathbf{u}\|_2 = 1$), the cosine similarity is computed efficiently via dot product. The search ranks chunks in descending order and returns the top-$k$ matches meeting the evidence threshold (&ge; 0.45).

---

### 7. Why Mozilla, Apache, and Eclipse?
These three open-source ecosystems are the canonical defect benchmarks specified by Infosys and academic software engineering literature (MSR Mining Software Repositories challenge). They represent mature, large-scale systems with authentic issue IDs, rich stack traces, multi-threading challenges, and documented git commit patches.

---

### 8. How is data processed?
The data pipeline executes:
$$\text{Raw JSON Ingestion} \rightarrow \text{Cleaning} \rightarrow \text{Normalization} \rightarrow \text{Deduplication} \rightarrow \text{Chunking} \rightarrow \text{Embedding} \rightarrow \text{Vector Index}$$
Records are cleaned of control characters, normalized into the canonical schema, chunked into semantically coherent blocks (preserving stack frames), converted into 384-dimensional dense vectors, and persisted to `rag/vector_index.pkl`.

---

### 9. How does Triage work?
The Triage Agent evaluates the defect text against empirical severity indicators (crash keywords, data loss, fatal signals), detects the affected subsystem via regex clustering, calculates priority from business impact, and derives a dynamic confidence score. It is architected to return varied severities and confidences based on input signals, never static constants.

---

### 10. Severity vs Priority?
- **Severity**: The technical impact of the defect on system stability (e.g., *Critical* = service down/data corruption; *Low* = cosmetic UI typo).
- **Priority**: The business urgency of resolving the defect (e.g., *High* = must be fixed immediately in current sprint; *Low* = can be addressed in future maintenance cycles).

---

### 11. How does Log Analysis work?
The Log Analysis Agent prioritizes **deterministic structural parsing**:
1. Checks for Python tracebacks (`File "...", line ...`).
2. Checks for Java exception frames (`at com.example...`).
3. Checks for Node.js / JavaScript call stacks (`at ... (file.js:12:34)`).
4. Checks for Go panic traces and kernel crash signals (`SIGSEGV`, `DeadlockDetected`).
5. Extracts exception type, error message, failure site, and stack frames.
It never hallucinates missing frames; if data is missing, it returns `null` or explicit notes.

---

### 12. How does Root Cause work?
The Root Cause Agent combines the deterministic log findings with RAG historical evidence. It operates under a **Four-Tier Attribution Guardrail**:
1. *Observed Facts*: Deterministic data directly verified from logs.
2. *Historical Evidence*: Retrieved precedent cases from knowledge base.
3. *AI Inference*: Causal deductive reasoning, clearly labelled as hypothesis.
4. *Fix Recommendation*: Actionable remediation strategy.

---

### 13. How does Duplicate Detection work?
The Duplicate Detection Agent compares the query vector against historical issues using the centralized similarity policy. If the top match achieves a cosine similarity $\ge 0.82$, it flags the bug as a **Likely Duplicate** and links the prior fix. If the score is between $0.65$ and $0.81$, it classifies it as a **Related Issue**, not a duplicate.

---

### 14. How are thresholds selected?
Thresholds were calibrated empirically across software crash texts:
- $\ge 0.82$: Identical or near-identical stack traces and failure sites.
- $0.65 &ndash; 0.81$: Defect in the same component or failure mode, but differing call sites.
- $0.45 &ndash; 0.64$: Weak architectural affinity.
- $< 0.45$: Unrelated or ungrounded queries; filtered out to prevent hallucinations.
All thresholds are configured centrally in `backend/config.py`.

---

### 15. How does Remediation work?
The Remediation Agent synthesizes the root cause hypothesis and precedent fix patches to formulate:
- An actionable summary statement.
- Technical explanation of why the fix works.
- Affected code location.
- Concrete drop-in code patch or configuration guard.
- Recommended automated verification tests (Unit, Concurrency, Regression).

---

### 16. How is hallucination controlled?
1. **Deterministic First**: Stack trace parsing is 100% deterministic regex/AST.
2. **Evidence Cutoff**: RAG queries below 0.45 return "Insufficient historical evidence found" rather than inventing records.
3. **Four-Tier Attribution**: Clear epistemic separation between empirical facts and AI inferences.
4. **Code is Source of Truth**: Metrics and charts are computed strictly from stored SQLite/PostgreSQL rows.

---

### 17. What happens with no historical match?
If no historical defect meets the 0.45 evidence cutoff, the RAG engine returns an empty evidence list. The Root Cause Agent explicitly notes `"Insufficient historical evidence found."`, and falls back to general engineering best practices without claiming historical precedent.

---

### 18. What happens if an agent fails?
The multi-agent orchestrator implements **graceful fault isolation**: each agent executes inside an isolated try-catch block measuring millisecond durations. If Stage 2 or 3 encounters an unexpected error, previous intermediate outputs (Triage, Submission) are preserved, the error is recorded in `context.errors`, and downstream agents proceed with partial context without crashing the application.

---

### 19. How are agents evaluated?
Against 10 ground-truth validation cases in `data/validation_dataset.json`. Real predictions are compared against ground truth to calculate:
- Severity Accuracy: 80.0%
- Priority Accuracy: 80.0%
- Duplicate Detection Accuracy: 80.0%
- Duplicate Detection Precision: 100.0% (Zero false duplicate alarms)
- Duplicate Detection Recall: 60.0%
- Duplicate Detection F1-Score: 75.0%
Metrics are generated directly by `scripts/evaluate_agents.py` into `reports/latest_evaluation.json`.

---

### 20. What are limitations?
- Local deterministic fallback relies on known patterns for deep semantic reasoning when external LLMs are disconnected.
- SQLite is used for lightweight local execution; enterprise production requires PostgreSQL + `pgvector`.
- Decompiling minified JavaScript or obfuscated bytecode requires source-map integration.

---

### 21. How does knowledge-base growth work?
To prevent memory pollution from incorrect automated hypotheses, only **human-verified bugs** can enter the permanent knowledge base. When an engineer verifies a diagnosis on the frontend, the system chunks the confirmed root cause and resolution, embeds it, and writes it to the active vector index.

---

### 22. What was the biggest technical challenge?
Ensuring cross-ecosystem consistency: handling heterogeneous crash dumps across Java, Python, and Node while maintaining mathematical reconciliation across analytics distributions and single-threshold policy enforcement.

---

### 23. What would be improved in production?
- Integration with live GitHub/GitLab webhooks and Jira APIs.
- Automated PR generation with branch checkout and test execution in sandboxed Docker containers.
- Fine-tuned domain embedding model trained on millions of MSR bug reports.
