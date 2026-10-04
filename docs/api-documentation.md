# API Documentation & REST Interface Specification

**Platform**: Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Base URL**: `/api`  
**Interactive Docs**: `/docs` (Swagger UI), `/redoc` (ReDoc)  
**Authentication**: Open for development / Bearer Token configurable via reverse proxy.

---

## 1. Health Check
### `GET /health`
Exposes application health, loaded vector index size, configured LLM provider, and the single centralized similarity policy thresholds.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "app": "Intelligent Bug Diagnosis Platform",
  "version": "1.0.0",
  "llm_provider": "fallback",
  "vector_index_size": 15,
  "similarity_policy": {
    "duplicate_threshold": 0.82,
    "related_threshold": 0.65,
    "weak_threshold": 0.45,
    "evidence_threshold": 0.45
  }
}
```

---

## 2. Bug Submission Endpoints

### `POST /api/submissions`
Submit bug report, stack trace, or log text with automatic input classification and sanitization.

**Request Body**:
```json
{
  "title": "NullPointerException in OrderProcessingService during checkout",
  "raw_content": "java.lang.NullPointerException: Cannot invoke ...",
  "input_type": "stack_trace",
  "environment_details": "Production JDK 17, Spring Boot 3.1.2"
}
```

**Response `201 Created`**:
```json
{
  "id": "7cc6f29b-7e5d-4bb3-8888-d625c3cac15f",
  "title": "NullPointerException in OrderProcessingService during checkout",
  "raw_content": "java.lang.NullPointerException: Cannot invoke ...",
  "input_type": "stack_trace",
  "environment_details": "Production JDK 17, Spring Boot 3.1.2",
  "status": "PENDING",
  "created_at": "2026-10-05T01:19:07.123456Z",
  "updated_at": "2026-10-05T01:19:07.123456Z"
}
```

### `POST /api/submissions/upload`
Upload a defect file (`.txt`, `.log`, `.md`, `.json`) up to 5 MB with zero-execution enforcement.

**Form Data**:
- `file`: Defect log file (binary stream)
- `title`: (Optional) Custom title
- `environment_details`: (Optional) System context

**Status Codes**:
- `201 Created`: Ingested successfully
- `413 Content Too Large`: File exceeds 5 MB ceiling
- `415 Unsupported Media Type`: Disallowed file extension
- `422 Unprocessable Content`: Empty or non-text file

### `GET /api/submissions`
List ingested defect submissions with pagination.
- Query parameters: `limit` (default: 50), `offset` (default: 0)

### `GET /api/submissions/{submission_id}`
Retrieve a single submission record by UUID.

---

## 3. Bug Diagnosis & Multi-Agent DAG Endpoints

### `POST /api/diagnosis/run/{submission_id}`
Triggers the multi-agent DAG pipeline:
`Triage Agent` &rarr; `Log Analysis Agent` &rarr; `RAG Retrieval Engine` &rarr; `Duplicate Detection Agent` &rarr; `Root Cause Agent` &rarr; `Remediation Agent`

**Response `200 OK` (`BugAnalysisContext`)**:
```json
{
  "submission_id": "7cc6f29b-7e5d-4bb3-8888-d625c3cac15f",
  "submission": { ... },
  "triage": {
    "severity": "High",
    "priority": "High",
    "affected_component": "Core / General System",
    "confidence": 0.86,
    "reasoning": "High severity functional breakdown...",
    "signals": ["nullpointerexception", "checkout"]
  },
  "log_analysis": {
    "exception_type": "java.lang.NullPointerException",
    "error_message": "Cannot invoke PaymentMethod.getToken()",
    "failure_point": "OrderProcessingService.java:142",
    "affected_code_path": "com.store.order.OrderProcessingService.executePayment",
    "stack_frames": [ ... ]
  },
  "rag_retrieval": [
    {
      "issue_id": "KAFKA-10134",
      "project": "Apache",
      "title": "NullPointerException in KafkaProducer",
      "similarity_score": 0.5196,
      "classification": "Weak Match",
      "fix_patch_summary": "Guard cluster.partition() with null check"
    }
  ],
  "duplicate_detection": {
    "is_duplicate": false,
    "top_matches": [ ... ],
    "duplicate_threshold": 0.82,
    "related_threshold": 0.65,
    "summary": "Weak historical correlation. Defect is considered novel."
  },
  "root_cause": {
    "hypothesis": "Unchecked dereference of uninitialized or null object reference...",
    "confidence": 0.91,
    "observed_facts": [ ... ],
    "historical_evidence": [ ... ],
    "ai_inference": [ ... ],
    "evidence_status": "sufficient"
  },
  "remediation": {
    "action": "Add defensive null validation and safe dereferencing guards",
    "explanation": "Prevents uncaught NullPointerException...",
    "affected_area": "OrderProcessingService.java:142",
    "code_patch": "if (targetObject == null) { return Collections.emptyList(); }",
    "recommended_tests": [ ... ]
  },
  "timeline": [
    { "stage_name": "Triage Agent", "duration_ms": 1.2, "status": "completed" },
    { "stage_name": "Log Analysis Agent", "duration_ms": 0.8, "status": "completed" },
    { "stage_name": "RAG Retrieval Engine", "duration_ms": 1.5, "status": "completed" },
    { "stage_name": "Duplicate Detection Agent", "duration_ms": 0.4, "status": "completed" },
    { "stage_name": "Root Cause Agent", "duration_ms": 0.9, "status": "completed" },
    { "stage_name": "Remediation Agent", "duration_ms": 0.7, "status": "completed" }
  ]
}
```

### `GET /api/diagnosis/{submission_id}`
Retrieve full canonical `BugAnalysisContext` for a previously completed analysis.

---

## 4. Historical Defect Knowledge Base Endpoints

### `GET /api/historical`
Retrieve indexed historical defect records with optional filtering.
- Query parameters:
  - `project`: Filter by ecosystem (`Mozilla`, `Apache`, `Eclipse`)
  - `severity`: Filter by severity (`Critical`, `High`, `Medium`, `Low`)
  - `search`: Keyword search in title, component, or issue ID
  - `limit`: Number of items (default: 50)
  - `offset`: Pagination offset (default: 0)

### `GET /api/historical/{issue_id}`
Retrieve authentic defect by upstream issue ID (e.g., `KAFKA-10134`, `MOZ-1689021`, `ECLIPSE-492012`).

### `POST /api/historical/search`
Perform 384-dimensional vector similarity search against indexed historical chunks.
- Request: `{"query": "database connection pool timeout deadlock", "top_k": 5}`
- Response: Array of `HistoricalEvidenceItem` with cosine similarity scores and classifications.

---

## 5. Defect Analytics Endpoints

### `GET /api/analytics`
Returns live system metrics with automated mathematical population reconciliation.
- Response includes:
  - `total_submissions`: Population $N_{sub}$
  - `completed_analyses`: Diagnosed cases
  - `pending_analyses`: Queue size
  - `duplicate_rate_percentage`: Rate of duplicates &ge; 0.82
  - `severity_distribution`: Strictly reconciled counts ($\sum Counts \equiv N_{sub}$)
  - `priority_distribution`: Strictly reconciled counts ($\sum Counts \equiv N_{sub}$)
  - `component_distribution`: Distribution of affected subsystems
  - `reconciliation_verified`: Boolean validation check

---

## 6. Knowledge Base Growth Endpoints

### `GET /api/knowledge-base`
List human-verified resolutions promoted into active RAG memory.

### `POST /api/knowledge-base/promote`
Promotes a verified diagnosis into active 384-dimensional vector memory:
- Request:
  ```json
  {
    "analysis_id": "7cc6f29b-7e5d-4bb3-8888-d625c3cac15f",
    "verified_by": "Lead QA Engineer",
    "verification_notes": "Tested fix in staging environment",
    "confirmed_root_cause": "Unchecked dereference of uninitialized payment method",
    "confirmed_resolution": "Added defensive null check and fallback token handler"
  }
  ```
- Action: Normalizes record, chunks content, generates dense embeddings, updates vector index, and saves to disk.
