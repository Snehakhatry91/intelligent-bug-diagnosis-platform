# Data Model & Population Reconciliation Specification

## Intelligent Bug Diagnosis Platform
**Organization:** Infosys Internship Evaluation Project  
**Author:** Software Architect  
**Copyright:** (c) 2025 Vidzai Digital (MIT License)  

---

## 1. Canonical In-Memory Context Model (`BugAnalysisContext`)

The multi-agent orchestration pipeline passes an immutable, strongly typed Pydantic model:

```python
class SubmissionContext(BaseModel):
    submission_id: str
    input_type: str  # "bug_report", "stack_trace", "error_log", "file_upload"
    submitted_at: str  # ISO-8601 UTC
    title: str
    content: str
    file_metadata: Optional[Dict[str, Any]] = None

class TriageResult(BaseModel):
    severity: Literal["Critical", "High", "Medium", "Low"]
    priority: Literal["High", "Medium", "Low"]
    affected_component: str
    confidence_score: float  # 0.0 - 1.0
    reasoning: str

class LogAnalysisResult(BaseModel):
    exception_type: str
    error_message: str
    failure_point: str
    affected_code_path: str
    key_signals: List[str] = []
    confidence_score: float

class RootCauseResult(BaseModel):
    hypothesis: str
    confidence_score: float
    observed_facts: List[str] = []
    historical_evidence: List[str] = []
    ai_inference: str

class DuplicateMatch(BaseModel):
    issue_id: str
    title: str
    project: str
    similarity_score: float
    classification: Literal["likely duplicate", "related issue", "weak match", "no meaningful match"]
    summary: Optional[str] = None
    historical_resolution: Optional[str] = None
    source: str

class DuplicateDetectionResult(BaseModel):
    classification: Literal["likely duplicate", "related issue", "weak match", "no meaningful match"]
    top_similarity_score: float = 0.0
    matches: List[DuplicateMatch] = []

class RecommendationItem(BaseModel):
    action: str
    affected_area: str
    implementation_guidance: str
    supporting_evidence: str
    confidence: float

class RemediationResult(BaseModel):
    recommendations: List[RecommendationItem] = []

class BugAnalysisContext(BaseModel):
    submission: SubmissionContext
    triage: Optional[TriageResult] = None
    log_analysis: Optional[LogAnalysisResult] = None
    root_cause: Optional[RootCauseResult] = None
    duplicate_detection: Optional[DuplicateDetectionResult] = None
    remediation: Optional[RemediationResult] = None
    processing_status: str = "completed"
    error_message: Optional[str] = None
```

---

## 2. Relational Database Tables (SQLAlchemy 2.0)

### 2.1 Table: `bug_submissions`
| Column Name | Type | Description |
|---|---|---|
| `id` | VARCHAR(36) PRIMARY KEY | Unique UUIDv4 identifier |
| `input_type` | VARCHAR(32) | `bug_report`, `stack_trace`, `error_log`, `file_upload` |
| `title` | VARCHAR(255) | Summary headline |
| `raw_content` | TEXT | Unadulterated textual payload |
| `file_name` | VARCHAR(255) NULLABLE | Original filename if uploaded |
| `file_size_bytes` | INTEGER NULLABLE | Size in bytes (max 5MB) |
| `status` | VARCHAR(32) | `received`, `triaged`, `completed`, `failed` |
| `created_at` | TIMESTAMP WITH TIME ZONE | UTC creation timestamp |

### 2.2 Table: `historical_defects`
| Column Name | Type | Description |
|---|---|---|
| `issue_id` | VARCHAR(100) PRIMARY KEY | Provenance issue ID (e.g. `MOZ-12870`, `KAFKA-10134`, `ECLIPSE-3322`) |
| `project` | VARCHAR(100) | Project name (e.g. `Mozilla`, `Apache Kafka`, `Eclipse Platform`) |
| `source` | VARCHAR(100) | Upstream bug tracker (`Mozilla Bugzilla`, `Apache Jira`, `Eclipse Bugzilla`) |
| `title` | VARCHAR(255) | Defect title from upstream tracker |
| `description` | TEXT | Description and failure details |
| `component` | VARCHAR(100) | Subsystem name |
| `severity` | VARCHAR(50) | `Critical`, `High`, `Medium`, `Low` |
| `priority` | VARCHAR(50) | `High`, `Medium`, `Low` |
| `status` | VARCHAR(50) | Upstream status (e.g. `VERIFIED`, `RESOLVED`, `CLOSED`) |
| `resolution` | VARCHAR(100) | Resolution status (e.g. `FIXED`) |
| `fix_patch_summary`| TEXT | Resolution and fix summary |
| `source_url` | VARCHAR(500) | Direct public bug tracker URL |
| `verified` | BOOLEAN | Provenance verification flag (`True`) |
| `data_type` | VARCHAR(50) | Data classification (`historical`) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Ingestion timestamp |

### 2.3 Table: `analysis_results`
| Column Name | Type | Description |
|---|---|---|
| `id` | VARCHAR(36) PRIMARY KEY | UUIDv4 identifier |
| `submission_id` | VARCHAR(36) FOREIGN KEY | Links to `bug_submissions.id` |
| `severity` | VARCHAR(32) | Triaged severity |
| `priority` | VARCHAR(32) | Triaged priority |
| `affected_component` | VARCHAR(64) | Triaged component |
| `exception_type` | VARCHAR(128) NULLABLE | Extracted exception class |
| `root_cause_hypothesis`| TEXT | Hypothesized root cause |
| `findings_json` | TEXT | Full serialized `BugAnalysisContext` JSON |
| `created_at` | TIMESTAMP WITH TIME ZONE | UTC execution timestamp |

### 2.4 Table: `knowledge_base_entries`
| Column Name | Type | Description |
|---|---|---|
| `id` | VARCHAR(36) PRIMARY KEY | UUIDv4 identifier |
| `submission_id` | VARCHAR(36) NULLABLE | Reference to original submission |
| `title` | VARCHAR(255) | Verified defect title |
| `root_cause` | TEXT | Confirmed root cause |
| `resolution` | TEXT | Confirmed resolution |
| `component` | VARCHAR(64) | Confirmed component |
| `verified_by` | VARCHAR(64) | Engineer name / signature |
| `is_verified` | BOOLEAN | Verification flag (True) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Ingestion timestamp |

---

## 3. Mathematical Population Reconciliation in Analytics

To guarantee complete consistency across all dashboard metrics:
1. **Submitted Defects Population ($N_{\text{sub}}$):**
   Count of all records in `bug_submissions`.
   $$\sum_{s \in \text{Severity Levels}} \text{Count}(s) \equiv N_{\text{sub}}$$
   $$\sum_{p \in \text{Priority Levels}} \text{Count}(p) \equiv N_{\text{sub}}$$
2. **Historical Defect Population ($N_{\text{hist}}$):**
   Total reference records in `historical_defects`.
3. **Verified Knowledge Base Population ($N_{\text{kb}}$):**
   Total verified records in `knowledge_base_entries`.
4. Automated reconciliation checks verify that no metric combines populations accidentally.
