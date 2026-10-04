# Infosys Agile Product Backlog

**Project Title**: Creation of Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance  
**Organization**: Infosys Internship Evaluation Project  

| Planned Sprint | Actual Sprint | US ID | User Story Description | MOSCOW | Dependency | Assignee | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Sprint 1 | Sprint 1 | US-01 | As an engineer, I need to submit defect reports via text and file upload up to 5MB with sanitization. | MUST | None | Full-Stack Dev | Done |
| Sprint 1 | Sprint 1 | US-02 | As a system, I need a canonical historical defect repository ingesting Mozilla, Apache, and Eclipse records. | MUST | None | Data / RAG Eng | Done |
| Sprint 1 | Sprint 1 | US-03 | As an engineer, I need a 384-dimensional dense semantic vector index with cosine similarity search. | MUST | US-02 | RAG Eng | Done |
| Sprint 2 | Sprint 2 | US-04 | As a triage lead, I need an automated Triage Agent to classify severity, priority, and component dynamically. | MUST | US-01 | AI / Agent Eng | Done |
| Sprint 2 | Sprint 2 | US-05 | As an engineer, I need a deterministic Log Analysis Agent to extract failure points and stack frames. | MUST | US-01 | Backend Eng | Done |
| Sprint 2 | Sprint 2 | US-06 | As an architect, I need a canonical `BugAnalysisContext` model shared across all downstream agents. | MUST | US-04, US-05 | Architect | Done |
| Sprint 2 | Sprint 2 | US-07 | As a system, I need a multi-agent orchestrator managing sequential DAG execution with fault tolerance. | MUST | US-06 | Backend Eng | Done |
| Sprint 3 | Sprint 3 | US-08 | As an engineer, I need a Root Cause Agent providing four-tier attribution (facts, evidence, inference, fix). | MUST | US-03, US-07 | AI Eng | Done |
| Sprint 3 | Sprint 3 | US-09 | As a QA lead, I need a Duplicate Detection Agent using a single central similarity policy (>=0.82 cutoff). | MUST | US-03, US-07 | RAG Eng | Done |
| Sprint 3 | Sprint 3 | US-10 | As an engineer, I need a Remediation Agent generating concrete code patches and automated test suites. | MUST | US-08 | AI Eng | Done |
| Sprint 3 | Sprint 3 | US-11 | As a developer, I need an enterprise dashboard to view complete analysis findings and raw JSON. | SHOULD | US-07 | Frontend Dev | Done |
| Sprint 4 | Sprint 4 | US-12 | As an engineering manager, I need defect pattern analytics with strict population reconciliation. | MUST | US-07 | Full-Stack Dev | Done |
| Sprint 4 | Sprint 4 | US-13 | As a lead engineer, I need human-in-the-loop knowledge base growth for verified bug resolutions. | SHOULD | US-03, US-08 | Full-Stack Dev | Done |
| Sprint 4 | Sprint 4 | US-14 | As an evaluator, I need 5 synthetic demo scenarios demonstrating all failure modes through the full DAG. | MUST | US-07, US-10 | QA / Full-Stack | Done |
| Sprint 4 | Sprint 4 | US-15 | As a QA engineer, I need automated pytest unit/integration test suites and live evaluation metrics. | MUST | US-07 | QA Eng | Done |
