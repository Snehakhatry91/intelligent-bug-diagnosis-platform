# Platform User Guide

Welcome to the Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance. This guide walks you through submitting bugs, analyzing diagnostic findings, reviewing historical precedents, and promoting verified solutions into system memory.

---

## 1. Submitting a Defect
1. Navigate to the **Submit Defect** tab in the top navigation bar.
2. Choose either **Direct Text / Stack Trace / Log** or **File Upload**.
3. Fill in:
   - **Defect Title**: A brief summary of the problem (e.g., `NullPointerException in OrderProcessingService`).
   - **Input Category**: Select Bug Report, Stack Trace, Error Log, or File Upload.
   - **Environment Context** (Optional): Specify operating system, runtime, or database version.
   - **Raw Content**: Paste the raw error log or stack trace, or drag-and-drop a file (`.txt`, `.log`, `.md`, `.json` up to 5 MB).
4. Click **Submit & Run Diagnosis**.

---

## 2. Interpreting Diagnostic Findings
Upon submission or selection from the Dashboard, the **Diagnosis Findings** page displays:
- **Triage Classification**: Severity badge (Critical, High, Medium, Low), Priority, and dynamic Confidence score derived from detected signals.
- **Deterministic Log Analysis**: Parsed exception signature, primary failure site (file and line number), affected code path, and decompiled stack frames.
- **Root Cause (Four-Tier Attribution)**:
  - *Observed Facts*: Empirical data from the crash log.
  - *Historical Evidence*: Retrieved citations from Mozilla, Apache, or Eclipse.
  - *AI Inference*: Logical deduction of the failure mechanism.
  - *Fix Recommendation*: Actionable engineering guidance.
- **Remediation Code Patch**: Drop-in code guard with a one-click copy button, accompanied by recommended unit and regression tests.
- **Historical Precedent Matches**: Similar defects with cosine similarity scores and direct links to upstream Bugzilla or Jira records.
- **Duplicate Status**: Clear indicator whether the bug is a likely duplicate (&ge; 82% similarity) or novel.
- **Raw JSON Context**: Full serializable state of the canonical context for API consumers.

---

## 3. Promoting Verified Bugs (Knowledge Base Growth)
1. In the **Diagnosis Findings** view, click **Promote to Verified KB**.
2. Enter your name (e.g., `Lead QA Engineer`) and brief verification notes.
3. Click **Confirm & Promote**.
4. The system automatically chunks the confirmed root cause and resolution, generates a 384-dimensional dense semantic embedding, and updates the persistent vector index.

---

## 4. Exploring Historical Defects & Analytics
- **Historical Defects**: Search and filter curated bug records from Mozilla Bugzilla, Apache Jira, and Eclipse Bugzilla by ecosystem and severity, or toggle **Vector Semantic Search** for dense similarity querying.
- **Defect Analytics**: Review real-time charts of severity distributions, priority allocation, affected components, and recurring exception types. The dashboard features automated mathematical verification proving that all distribution counts reconcile to the total submitted population.
