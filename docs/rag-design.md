# Retrieval-Augmented Generation (RAG) Architecture & Vector Pipeline

## Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance
**Organization:** Infosys Internship Evaluation Project  
**Author:** AI/ML & RAG Engineer  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. RAG Technical Specifications Summary

| Parameter | Specification | Implementation Details |
| :--- | :--- | :--- |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` | Open-source dense SentenceTransformer executed locally on CPU/GPU without external API keys |
| **Vector Dimension** | `384` | 384-dimensional dense float32 vector per chunk |
| **Similarity Metric** | `Cosine Similarity` | $\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$ (equivalent to dot product since $\|\mathbf{v}\|_2 = 1.0$) |
| **Vector Index** | `rag/vector_index.pkl` | Persistent local binary serialization storing chunk texts, metadata, model name, dimension, version, and creation timestamp |
| **Retrieval Engine** | `rag/retrieval_engine.py` | In-memory matrix multiplication over normalized NumPy embedding matrix |
| **Evidence Threshold** | `0.45` | Queries with similarity $< 0.45$ strictly return `"Insufficient historical evidence found"` |
| **Duplicate Threshold**| `0.82` | Queries with similarity $\ge 0.82$ flagged as `"Likely Duplicate"` |
| **Related Threshold**  | `0.65` | Similarities between $0.65$ and $0.81$ classified as `"Related Issue"` |

---

## 2. Problem Formulation & Grounding Philosophy

In standard LLM diagnostic tools, models frequently hallucinate non-existent API parameters, incorrect error causes, and fabricated issue numbers. In this platform, RAG acts as an **empirical grounding anchor**:
1. Incoming bug submissions and stack traces are preprocessed and converted into dense 384-dimensional vector queries.
2. The RAG engine retrieves historical defect records from verified public open-source repositories (Mozilla Bugzilla, Apache Jira, Eclipse Bugzilla).
3. Downstream Root Cause and Remediation Agents reason strictly over verified historical resolutions rather than generating ungrounded assumptions.
4. If no historical record is sufficiently similar ($< 0.45$), the platform returns an explicit negative statement rather than fabricating evidence.

---

## 3. Ingestion, Cleaning & Chunking Pipeline

```
Raw Defect Repositories (Mozilla, Apache, Eclipse)
                   │
                   ▼
     Stage 1: Field Extraction & Provenance Normalization
       - Normalize fields: id, project, source_issue_id, title, description,
         component, resolution, resolution_summary, verified, source_url
                   │
                   ▼
     Stage 2: Cleaning & Validation
       - Validate source provenance via scripts/validate_historical_data.py
       - Ensure non-empty description, real upstream URLs, verified=true
                   │
                   ▼
     Stage 3: Domain-Aware Chunking
       - Symptom Chunk: Issue ID + Component + Title + Description
       - Resolution Chunk: Issue ID + Component + Resolution Summary
                   │
                   ▼
     Stage 4: Dense Vector Embedding
       - Model: sentence-transformers/all-MiniLM-L6-v2 (local execution)
       - 384-dimensional dense semantic vectors
       - Unit L2 normalization: ||v|| = 1.0
                   │
                   ▼
     Stage 5: Persistent Vector Indexing
       - Stored in rag/vector_index.pkl with index version metadata:
         {kb_version: "1.0.0", model: "all-MiniLM-L6-v2", dimension: 384, metric: "cosine", timestamp: UTC}
       - Automatic incompatible-index detection rejecting mismatched models
```

---

## 4. Single Unified Similarity Policy

To prevent contradictory classifications across agents, the platform enforces **one central similarity policy** configured in `backend/config.py`:

| Threshold Range | Match Classification | Diagnostic Action |
|---|---|---|
| **$S_C \ge 0.82$** | **Likely Duplicate** | High semantic overlap; surfaces historical resolution and alerts engineer against redundant ticket filing. |
| **$0.65 \le S_C < 0.82$** | **Related Issue** | Contextual alignment in same component/failure mode; provides historical resolution summary as context. |
| **$0.45 \le S_C < 0.65$** | **Weak Match** | Partial technical keyword or stack frame overlap; displayed as secondary background reference. |
| **$S_C < 0.45$** | **Insufficient Historical Evidence** | Query lacks sufficient semantic affinity to any historical defect. Engine returns: `"Insufficient historical evidence found"`. |

---

## 5. Mathematical Retrieval Algorithm

1. **Query Encoding:** Given incoming defect text $q$, compute normalized query vector:
   $$\mathbf{u} = \frac{\text{embed}(q)}{\|\text{embed}(q)\|_2} \in \mathbb{R}^{384}$$
2. **Batch Similarity Computation:** Given normalized historical matrix $\mathbf{V} \in \mathbb{R}^{N \times 384}$:
   $$\mathbf{s} = \mathbf{V} \mathbf{u}^\top \in \mathbb{R}^N$$
3. **Filtering & Ranking:**
   - Filter candidates where $s_i < 0.45$.
   - Sort remaining candidates in descending order: $s_{(1)} \ge s_{(2)} \ge \dots \ge s_{(k)}$.
   - Return top-$k$ matches (default $k=3$) with associated metadata (issue ID, project, source URL, resolution summary).

---

## 6. Vector Store Implementation Architecture

### Current Evaluation Implementation
For the current evaluation prototype, historical defect embeddings are stored in a persistent local vector index (`rag/vector_index.pkl`) and compared using cosine similarity via NumPy. This keeps the project fully local, reproducible, and cost-free without requiring external vector database daemons.

- **Storage Location**: `rag/vector_index.pkl`
- **Embedding Matrix**: Normalized float32 matrix $\mathbf{V} \in \mathbb{R}^{15 \times 384}$
- **Retrieval Mechanism**: In-memory matrix multiplication ($\mathbf{V} \mathbf{u}^\top$)
- **Safeguards**:
  - **Version Compatibility Check:** On load, `rag/vector_store.py` verifies that the index metadata matches the current model (`all-MiniLM-L6-v2`), dimension (`384`), and KB version.
  - **Graceful Regeneration:** If the index is missing or incompatible, the system refuses to load stale embeddings and prompts the operator to run `python scripts/ingest_historical_data.py`.

### Future Production Scaling Option
The architecture can be migrated to PostgreSQL with `pgvector` or another production vector database (such as Qdrant or Milvus) for larger-scale enterprise deployments:
- **Relational + Vector Hybrid**: PostgreSQL with `CREATE EXTENSION vector;` storing both structured defect metadata and HNSW/IVFFlat vector indexes.
- **Distributed Sharding**: Dedicated vector search clusters handling millions of defect embeddings with horizontal replica scaling.
- The `VectorStore` interface is cleanly decoupled, enabling drop-in migration without modifying agent reasoning logic.
