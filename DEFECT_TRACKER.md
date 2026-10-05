# Infosys Defect Tracker (Empirical Internal Defects)

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Allowed Types**: Logical, User Interface, Maintainability, Standards, Others  
**Rule**: Documents actual engineering defects encountered and resolved during system implementation and testing.

| Sl No | Submitted By | Submitted Date | Description | Detected Sprint | Assigned To | Type Of Defect | Action Taken | Action Taken Date | Status | Remarks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Full-Stack Dev | 2026-09-02 | Pydantic Settings raised SettingsError when loading comma-delimited strings from `.env` for `ALLOWED_EXTENSIONS`. | Sprint 1 | Backend Dev | Logical | Added `@field_validator` in `backend/config.py` to parse both JSON lists and comma-separated tokens. | 2026-09-02 | Closed | Resolved; unit tests pass. |
| 2 | QA Eng | 2026-09-04 | Ingestion script crashed with `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'` on Windows cp1252. | Sprint 1 | Backend Dev | Standards | Replaced unicode checkmarks with cross-platform ASCII indicators `[OK]` and `[WARN]`. | 2026-09-04 | Closed | Verified on Windows PowerShell. |
| 3 | QA Eng | 2026-09-16 | Python 3.12 emitted DeprecationWarning for `datetime.utcnow()`. | Sprint 2 | Backend Dev | Standards | Replaced all instances of `datetime.utcnow()` with `datetime.now(timezone.utc)`. | 2026-09-16 | Closed | Zero deprecation warnings in test suite. |
| 4 | AI Eng | 2026-09-22 | Orchestrator timeline was not populated because Pydantic v2 instantiated an isolated copy of the timeline list. | Sprint 2 | Backend Dev | Logical | Refactored orchestrator to append stage telemetries directly onto `context.timeline`. | 2026-09-22 | Closed | Timeline correctly records all 6 stages. |
| 5 | QA Eng | 2026-09-25 | `JAVA_EXCEPTION` regex matched lines starting with `Exception in thread "main"` improperly as unstructured text. | Sprint 2 | Backend Dev | Logical | Enhanced Java exception regex to explicitly recognize `Exception in thread "..."` prefixes. | 2026-09-25 | Closed | `test_parse_java_null_pointer_trace` passes. |
| 6 | Frontend Dev | 2026-10-05 | Vite TypeScript build failed with error TS1382 due to unescaped `>=` symbol in JSX text in `HistoricalDefectsPage.tsx`. | Sprint 3 | Frontend Dev | User Interface | Replaced raw `>=` character with valid HTML entity `&ge;`. | 2026-10-05 | Closed | Production bundle built cleanly in 2.06s. |
| 7 | Full-Stack Dev | 2026-10-05 | FastAPI raised ResponseValidationError on `GET /api/historical` because `HistoricalDefectSchema.created_at` expected `str` instead of `DateTime`. | Sprint 3 | Full-Stack Dev | Logical | Updated `created_at` type annotation to `Optional[Any]` in `backend/models/schemas.py`. | 2026-10-05 | Closed | Endpoint returns 200 with ISO datetime. |
