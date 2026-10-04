# Infosys Unit Test Plan & Execution Results

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Execution Command**: `python -m pytest tests -v`  
**Execution Summary**: 25 executed, 25 passed, 0 failed, 0 errors in 0.97s (100% Pass Rate)

| Sl No | Test Case Name | Test Procedure | Condition to be tested | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `test_health_check_endpoint` | Send GET request to `/health` endpoint | Verify system status, app name, and similarity policy thresholds are returned | HTTP 200, status="healthy", duplicate_threshold=0.82 | **PASSED** |
| 2 | `test_submit_and_diagnose_pipeline_api` | Send POST `/api/submissions` then POST `/api/diagnosis/run/{id}` | Ingest bug, trigger full DAG pipeline, verify populated context | HTTP 201 on submit, HTTP 200 on diagnosis with non-null root cause & fix | **PASSED** |
| 3 | `test_historical_defects_api` | Send GET `/api/historical?project=Mozilla` | Filter defect repository by Mozilla ecosystem | HTTP 200, array of Mozilla defects returned with issue IDs | **PASSED** |
| 4 | `test_analytics_api_endpoint` | Send GET `/api/analytics` | Retrieve defect telemetry and automated reconciliation verification flag | HTTP 200, `reconciliation_verified=True`, distribution matches population | **PASSED** |
| 5 | `test_orchestrator_full_dag_execution` | Instantiate `DiagnosticOrchestrator` and run `execute_diagnosis(sub)` | Execute all 6 stages sequentially, record timing telemetries | Non-null triage, log analysis, duplicate detection, root cause, and remediation | **PASSED** |
| 6 | `test_triage_agent_produces_variable_severities_and_confidences` | Process Critical crash text vs Low cosmetic typo | Verify agent dynamically outputs distinct severities & confidence scores | Critical severity (conf >= 0.90) != Low severity (conf <= 0.80) | **PASSED** |
| 7 | `test_duplicate_detection_agent_threshold_gating` | Evaluate evidence items with score 0.88 vs 0.72 | Check single central similarity policy (>= 0.82 cutoff) | Score 0.88 -> `is_duplicate=True`; Score 0.72 -> `is_duplicate=False` | **PASSED** |
| 8 | `test_root_cause_agent_four_tier_attribution` | Run `root_cause_agent.process(context)` | Verify 4-tier attribution separation (observed facts, evidence, inference) | Hypothesis populated, observed facts listed, historical evidence recorded | **PASSED** |
| 9 | `test_remediation_agent_generates_concrete_patch_and_tests` | Run `remediation_agent.process(context)` | Generate concrete actionable fix recommendation and test plan | Action specified, code patch snippet provided, unit tests included | **PASSED** |
| 10 | `test_analytics_population_reconciliation` | Query `AnalyticsService.get_analytics_summary(db)` | Verify $\sum Counts \equiv Total Submissions$ | `sum(severity_counts) == total_submissions`, `reconciliation_verified=True` | **PASSED** |
| 11 | `test_parse_java_null_pointer_trace` | Parse Java NPE stack trace with `Exception in thread "main"` | Extract exception type, error message, failure point, and stack frames | Exception="java.lang.NullPointerException", 2 stack frames extracted | **PASSED** |
| 12 | `test_parse_python_traceback` | Parse Python Traceback dump | Extract Python exception signature, line number, and function | Exception="ValueError", failure_point="/app/backend/models.py:120" | **PASSED** |
| 13 | `test_parse_node_javascript_error` | Parse Node.js TypeError trace | Extract JavaScript error type and stack frames | Exception="TypeError", failure_point="/usr/src/app/auth.js:45" | **PASSED** |
| 14 | `test_parse_system_signal` | Parse kernel crash log with SIGSEGV | Detect system signal pattern without stack frames | Exception="SIGSEGV", key_log_signals contains "SIGSEGV" | **PASSED** |
| 15 | `test_parse_empty_content_returns_non_hallucinated_defaults` | Parse empty string `""` | Verify non-hallucinated defaults and explanation notes | `exception_type=None`, `failure_point=None`, stack_frames=[] | **PASSED** |
| 16 | `test_chunk_defect_record_preserves_canonical_metadata` | Chunk historical defect dictionary with `text_chunker` | Preserve issue ID, project, component, and title in chunk metadata | Primary chunk contains issue ID, project, and summary text | **PASSED** |
| 17 | `test_embedder_generates_384_dim_unit_vectors` | Generate dense embedding for defect text | Verify dimension is 384 and vector norm equals 1.0 | Vector shape == (384,), L2 norm == 1.0 within 1e-3 | **PASSED** |
| 18 | `test_cosine_similarity_calculation` | Calculate cosine similarity between identical texts | Dot product of unit vectors equals 1.0 | Cosine similarity == 1.0 within 1e-4 | **PASSED** |
| 19 | `test_retrieval_engine_similarity_policy_classification` | Classify similarity scores (0.85, 0.82, 0.70, 0.65, 0.50, 0.40) | Check classifications against single central similarity policy | 0.85 -> Likely Duplicate, 0.70 -> Related, 0.50 -> Weak, 0.40 -> No Match | **PASSED** |
| 20 | `test_retrieval_returns_insufficient_evidence_for_novel_query` | Query vector store with non-bug recipe text | Score falls below 0.45 threshold | Returns empty list and "Insufficient historical evidence found" | **PASSED** |
| 21 | `test_sanitize_text_strips_null_bytes_and_control_chars` | Sanitize string containing `\x00` and control characters | Strip destructive bytes while preserving `\n` and `\t` | Clean text returned without null bytes | **PASSED** |
| 22 | `test_submission_rejects_empty_or_short_title` | Instantiate `SubmissionCreate` with title `"  "` | Pydantic validation rejects title < 3 chars | Raises Pydantic `ValidationError` | **PASSED** |
| 23 | `test_file_upload_rejects_unallowed_extension` | Upload file `malicious_payload.exe` | Enforce allowed extensions (`.txt`, `.log`, `.md`, `.json`) | HTTP 415 Unsupported Media Type | **PASSED** |
| 24 | `test_file_upload_rejects_empty_file` | Upload 0-byte file `empty.log` | Validate non-empty payload | HTTP 422 Unprocessable Content | **PASSED** |
| 25 | `test_file_upload_enforces_5mb_ceiling` | Upload 5MB + 1 byte file `giant.log` | Enforce 5MB size limit | HTTP 413 Content Too Large | **PASSED** |
