# Infosys Agile Daily Stand-Up Meeting Log

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Sprint Structure**: 4 Sprints &times; 14 Days

| Sprint | Day | Impediments | Action Taken |
| :--- | :--- | :--- | :--- |
| Sprint 1 | Day 1 | Windows console cp1252 character mapping error when printing Unicode checkmarks in ingestion CLI. | Replaced Unicode glyphs with robust ASCII status identifiers (`[OK]`, `[WARN]`, `[INFO]`). |
| Sprint 1 | Day 3 | Pydantic Settings failing to parse comma-delimited environment strings into list types. | Implemented custom `@field_validator` in `backend/config.py` to support JSON arrays and comma-separated tokens. |
| Sprint 1 | Day 7 | High-volume raw dataset downloads from Bugzilla can stall without network timeouts. | Created canonical JSON schema files and provided verified offline sample datasets with automated validation. |
| Sprint 2 | Day 2 | Python 3.12 emitting deprecation warnings for `datetime.utcnow()`. | Refactored all model defaults and timestamps to use timezone-aware `datetime.now(timezone.utc)`. |
| Sprint 2 | Day 5 | Overlapping regex patterns in deterministic parser causing Java exception signatures to intercept Python traces. | Established strict mutual exclusion order prioritizing Python tracebacks before Java/Node stack inspections. |
| Sprint 2 | Day 9 | Pydantic v2 creating shallow validation copies of list fields preventing in-place context mutation. | Refactored orchestrator to append stage telemetries directly onto `context.timeline` and `context.errors`. |
| Sprint 3 | Day 3 | Cosine similarity scoring fluctuating on unnormalized vectors. | Enforced L2 unit-norm normalization ($v = v / \|v\|_2$) ensuring exact mathematical cosine equivalence. |
| Sprint 3 | Day 6 | Semantic retrieval returning weak matches below acceptable evidence threshold. | Implemented strict cutoff at `EVIDENCE_THRESHOLD = 0.45` returning "Insufficient historical evidence found". |
| Sprint 3 | Day 11 | Vite React TypeScript strict checks failing on unescaped `>` in JSX text. | Replaced raw inequality symbols with valid HTML entities (`&gt;=`) and updated TypeScript app config. |
| Sprint 4 | Day 2 | Potential discrepancy between submission totals and severity distributions. | Implemented automated population reconciliation assertions in `analytics_service.py` verifying $\sum Counts \equiv Total$. |
| Sprint 4 | Day 6 | Pytest asyncio failing on async test fixture scopes. | Configured `pytest.ini` with `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = function`. |
| Sprint 4 | Day 10 | Verification of 5 synthetic demo scenarios against authentic historical defect distinction. | Maintained separate fixture directory `tests/fixtures/demo_scenarios.json` clearly marked as synthetic demonstration data. |
| Sprint 4 | Day 14 | Preparing final demonstration and technical documentation. | Audited all endpoints, re-executed 25 unit/integration tests with 100% pass rate, and generated reports. |
