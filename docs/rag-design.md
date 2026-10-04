# Retrieval-Augmented Generation (RAG) Architecture & Vector Pipeline

## Intelligent Bug Diagnosis Platform
**Organization:** Infosys Internship Evaluation Project  
**Author:** AI/ML & RAG Engineer  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. RAG Foundations & Problem Formulation

In naive LLM diagnostic systems, language models frequently hallucinate non-existent API parameters, incorrect error causes, and fabricated issue numbers. In this platform, RAG acts as an **empirical grounding anchor**:
1. Incoming bug submissions and stack traces are converted into dense vector queries.
2. The RAG engine retrieves historical defect records from verified open-source repositories (Mozilla, Apache, Eclipse).
3. The Root Cause and Remediation Agents reason strictly over verified historical resolutions rather than generating ungrounded assumptions.

---

## 2. Ingestion, Cleaning & Chunking Pipeline

```
Raw Defect Repositories (Mozilla, Apache, Eclipse)
                   │
                   ▼
     Stage 1: Field Extraction & Normalization
       - Normalize fields: issue_id, project, title, description, component,
         severity, priority, status, resolution, fix_patch, source_url
                   │
                   ▼
     Stage 2: Cleaning & Deduplication
       - Strip HTML boilerplate and normalize line breaks
       - Standardize severity: Critical, High, Medium, Low
       - Eliminate redundant records via content hashing
                   │
                   ▼
     Stage 3: Domain-Aware Chunking
       - Primary Symptoms Chunk: Issue ID + Component + Severity + Title + Description
       - Resolution Fix Chunk: Issue ID + Resolution Diagnosis + Code Patch
                   │
                   ▼
     Stage 4: Dense Vector Embedding
       - 384-dimensional dense semantic vectors
       - Unit L2 normalization: ||v|| = 1.0
                   │
                   ▼
     Stage 5: Persistent Vector Indexing
       - Stored in pgvector (PostgreSQL) or local cosine vector index (SQLite)
```

---

## 3. Single Unified Similarity Policy

To ensure absolute consistency across all agents, APIs, and tests, the platform defines **one central similarity policy**:

| Threshold Range | Match Classification | Diagnostic Action |
|---|---|---|
| **$S_C \ge 0.82$** | **Likely Duplicate** | High semantic overlap; surfaces historical resolution and alerts engineer against redundant filing. |
| **$0.65 \le S_C < 0.82$** | **Related Issue** | High contextual alignment (same component/subsystem); provides historical workarounds. |
| **$0.45 \le S_C < 0.65$** | **Weak Match** | Partial technical keyword or frame overlap; displayed as secondary reference. |
| **$S_C < 0.45$** | **No Meaningful Match** | Novel defect. Engine explicitly reports: `"Insufficient historical evidence found"`. |

---

## 4. Anti-Hallucination Framework

1. **Empirical Cutoff:** If the top-scoring candidate has a cosine similarity score $< 0.45$, the RAG engine returns empty evidence and the explicit message: `"Insufficient historical evidence found"`.
2. **Explicit 4-Tier Attribution:**
   - **OBSERVED FACT:** Empirically verified tokens from the user input (e.g. `NullPointerException at TokenAuthFilter.java:84`).
   - **HISTORICAL EVIDENCE:** Quoted records from Mozilla, Apache, or Eclipse with verifiable IDs.
   - **AI INFERENCE:** Deductive reasoning connecting facts to evidence.
   - **FIX RECOMMENDATION:** Concrete code patch or configuration fix.
3. **Deterministic AST Parsing First:** Stack frames, line numbers, and exception names are extracted via deterministic grammars prior to vector retrieval.
