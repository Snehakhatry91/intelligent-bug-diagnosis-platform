# Infosys Agile Sprint Retrospectives

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Evaluation Program**: Infosys Internship Evaluation Project

| SL # | Sprint # | Sprint start date | Sprint end date | Team member name | Start Doing | Stop Doing | Continue Doing | Action taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Sprint 1 | 2026-09-01 | 2026-09-14 | Engineering Lead | Pre-validating console character encoding before CLI output. | Assuming UTF-8 console output is universal across Windows PowerShell. | Using strongly-typed Pydantic settings with explicit env defaults. | Replaced Unicode terminal glyphs with cross-platform ASCII indicators. |
| 2 | Sprint 2 | 2026-09-15 | 2026-09-28 | Backend Architect | Directly appending to Pydantic context attributes during DAG execution. | Creating intermediate local lists that get disconnected by model validation. | Designing canonical contexts with comprehensive telemetry capture. | Refactored multi-agent orchestrator lifecycle methods to mutate context directly. |
| 3 | Sprint 3 | 2026-09-29 | 2026-10-12 | RAG / AI Engineer | Enforcing single centralized similarity policy across all agents. | Hardcoding disparate cosine thresholds in individual agent files. | Clearly distinguishing observed facts from AI inferences. | Unified similarity thresholds in `backend/config.py` with 0.82 duplicate cutoff. |
| 4 | Sprint 4 | 2026-10-13 | 2026-10-26 | QA / Full-Stack | Automating mathematical population reconciliation assertions in CI. | Reporting metrics without verifying population balance formulas. | Measuring real test and latency numbers from actual CLI executions. | Built automated verification flag into Analytics API and executed 25/25 pytest suite. |
