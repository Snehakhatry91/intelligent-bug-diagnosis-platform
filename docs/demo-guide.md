# Final Demonstration Walkthrough Guide

This document outlines the exact 18-step evaluation demonstration flow for presentation to the Infosys evaluation committee.

---

## Preparation
1. Start Backend:
   ```bash
   python -m uvicorn backend.main:app --port 8000
   ```
2. Start Frontend:
   ```bash
   cd frontend && npm run dev
   ```
3. Open browser at `http://localhost:5173`.

---

## Step-by-Step Demonstration Sequence

### Step 1: Open Application
- Open `http://localhost:5173`. Point out the modern dark glassmorphism design, brand logo, and the green "Engine Online" indicator connected to `/health`.

### Step 2: Show Dashboard
- Highlight the 5 top KPI cards: Total Submissions, Completed Diagnoses, Historical Knowledge (15 curated records), Duplicate Rate, and Verified Solutions.
- Point out the 5 Required Synthetic Demonstration Scenarios cards.

### Step 3: Submit a Bug
- Click **Submit Defect** in the navbar or click "Submit Defect for Diagnosis" from the hero banner.

### Step 4: Paste or Upload Stack Trace / Log
- Click the **Java NPE Stack Trace** sample button (or drag and drop a `.log` file).
- Note the automatic population of Title, Input Category, Environment Context, and raw stack trace.
- Point out that the system enforces a 5MB size limit, allowed extensions, and null-byte sanitization.

### Step 5: Start Analysis
- Click **Submit & Run Diagnosis**.
- Note the real-time processing indicator while the orchestrator executes the 6-stage DAG.

### Step 6: Show Triage Agent Findings
- Show the diagnosed **Severity (High)**, **Priority (High)**, and dynamic **Confidence score (86%)**.
- Highlight the **Triage Reasoning** and the extracted empirical crash signals (`nullpointerexception`, `checkout`).
- Emphasize that triage outputs are dynamic and vary according to actual submission content.

### Step 7: Show Log Analysis Agent Findings
- Show the parsed exception signature (`java.lang.NullPointerException`).
- Show the primary failure site (`OrderProcessingService.java:142`) and affected code path (`executePayment`).
- Expand the decompiled stack frames list.

### Step 8: Show Historical Evidence (RAG)
- Show the retrieved precedent matches from the vector index.
- Point out the similarity score, project (`Apache HTTPCLIENT-2099` / `CASSANDRA-2189`), and the resolution summary.

### Step 9: Show Root Cause Agent
- Show the **Root Cause Hypothesis**.
- Point out the **Four-Tier Attribution Guardrail**:
  1. *Observed Facts*
  2. *Historical Evidence*
  3. *AI Inference*
  4. *Fix Recommendation*
- Explain how this strictly prevents hallucinations.

### Step 10: Show Duplicate Detection Agent
- Show the Duplicate Status badge. Explain the centralized &ge; 0.82 threshold policy.
- Note that this specific bug is diagnosed as **Novel (Not a Duplicate)** because its similarity score (52%) falls below the 0.82 threshold.

### Step 11: Show Remediation Agent
- Show the actionable engineering summary.
- Show the concrete **Code Patch** snippet with the copy button.
- Show the recommended automated verification tests (Unit Test, Regression Test).

### Step 12: Show Structured Findings & Raw JSON
- Switch tabs to **Raw JSON Context**. Show that the complete strongly-typed `BugAnalysisContext` is available for integration.

### Step 13: Show Defect Analytics
- Click **Defect Analytics** in the navbar.
- Point out the **Mathematical Population Reconciliation Banner**:
  $\text{Total Submissions} \equiv \sum \text{Severity Counts} \equiv \sum \text{Priority Counts}$.
- Show the interactive Recharts charts (Severity Pie, Priority Bar, Component Breakdown, Exception Types).

### Step 14: Demonstrate Another Bug
- Return to Dashboard and click on **DEMO-02: Database Connection Pool Saturated Deadlock**.
- Note the resulting **Critical Severity**, affected component (**Database / Persistence**), and non-blocking timeout fix.

### Step 15: Demonstrate Novel Defect vs. Duplicate Detection
- Return to Dashboard and click on **DEMO-03: JWT Bearer Authentication Token Expiration**.
- Note the resulting **Medium Severity**, affected component (**Authentication / Security**), and header-normalization remediation.
- To demonstrate duplicate detection, navigate to Submit Defect and paste an issue matching an indexed historical defect (such as `VAL-001` / `MOZ-12870` or `VAL-005` / `ECLIPSE-3322`). Show that it scores $\ge 0.82$ similarity against the historical index and is correctly flagged as a **Likely Duplicate** (&ge; 82%).

### Step 16: Show Knowledge Base Growth (Self-Improving Memory)
- In the diagnosis view, click **Promote to Verified KB**.
- Enter verifier name: `Lead Evaluator` and notes: `Verified fix in local regression suite`.
- Click **Confirm & Promote**.
- Navigate to **Verified Knowledge Base** to show the newly indexed record and explain how human verification prevents memory pollution.

### Step 17: Show Empirical Evaluation & Testing Benchmarks
- Navigate to **Empirical Evaluation**.
- Review the measured metrics: **80.0% Severity Accuracy**, **80.0% Priority Accuracy**, **100% Duplicate Precision**, **60% Duplicate Recall**, **75.0% F1-Score**.
- Show the Duplicate Detection Confusion Matrix and the case-by-case audit log.

### Step 18: Explain System Architecture
- Navigate to **Documentation**.
- Walk through the Multi-Agent Orchestration DAG, the single centralized similarity policy table, and the historical dataset provenance.
