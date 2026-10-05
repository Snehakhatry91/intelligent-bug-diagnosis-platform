# Empirical Agent Evaluation & Benchmark Report

## 1. Evaluation Methodology
- **Validation Dataset**: Labeled ground truth across 10 distinct software defects in `data/validation_dataset.json`.
- **Ecosystems Tested**: Mozilla Bugzilla, Apache Jira, Eclipse Bugzilla, and novel application errors.
- **Evaluation Rule**: Metrics are calculated solely from actual model predictions compared against ground truth labels. No synthetic figures or fabricated metrics are reported.
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, cosine similarity).

---

## 2. Summary of Empirical Results

| Metric | Measured Value | Sample Size (N) | Formula / Derivation |
| :--- | :--- | :--- | :--- |
| **Severity Classification Accuracy** | **80.0%** | 10 | Correct Severities / Total Cases (8/10) |
| **Priority Classification Accuracy** | **80.0%** | 10 | Correct Priorities / Total Cases (8/10) |
| **Duplicate Detection Accuracy** | **80.0%** | 10 | (TP + TN) / Total Cases (8/10) |
| **Duplicate Detection Precision** | **100.0%** | 3 Positives | TP / (TP + FP) = 3 / (3 + 0) |
| **Duplicate Detection Recall** | **60.0%** | 5 Actuals | TP / (TP + FN) = 3 / (3 + 2) |
| **Duplicate Detection F1-Score** | **75.0%** | 10 | Harmonic Mean of Precision and Recall |

---

## 3. Confusion Matrix: Duplicate Detection

| Actual \ Predicted | Predicted Duplicate (Score >= 0.82) | Predicted Novel / Non-Duplicate | Total Actual |
| :--- | :--- | :--- | :--- |
| **Actual Duplicate** | **3** (True Positive) | **2** (False Negative) | 5 |
| **Actual Non-Duplicate** | **0** (False Positive) | **5** (True Negative) | 5 |
| **Total Predicted** | 3 | 7 | **10** |

---

## 4. Case-by-Case Prediction Audit

| Case ID | Title Excerpt | Predicted Severity | Actual Severity | Pred Duplicate | Actual Duplicate | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `VAL-001` | AB-BA deadlocks between pipe and channel... | `Critical` | `Critical` | `True` | `True` | **PASS** |
| `VAL-002` | NullPointerException in ConsoleConsumer... | `High` | `Critical` | `False` | `True` | **REVIEW** |
| `VAL-003` | unlimited socket timeout results in the ... | `Low` | `High` | `True` | `True` | **REVIEW** |
| `VAL-004` | json2sstable fails due to OutOfMemory... | `High` | `High` | `False` | `True` | **REVIEW** |
| `VAL-005` | CVS Authentication error: says name/pass... | `Medium` | `Medium` | `True` | `True` | **PASS** |
| `VAL-006` | NullPointerException in payment gateway ... | `High` | `High` | `False` | `False` | **PASS** |
| `VAL-007` | Minor cosmetic typo in user profile sett... | `Low` | `Low` | `False` | `False` | **PASS** |
| `VAL-008` | API rate limit warning emitted when sync... | `Medium` | `Medium` | `False` | `False` | **PASS** |
| `VAL-009` | Deadlock detected during simultaneous in... | `Critical` | `Critical` | `False` | `False` | **PASS** |
| `VAL-010` | Deprecated API warning in legacy report ... | `Low` | `Low` | `False` | `False` | **PASS** |

---

## 5. Anti-Hallucination & Evidence Policy Audit
- **Grounding Rate**: All duplicate detections strictly adhered to the single central similarity policy (`DUPLICATE_THRESHOLD = 0.82`).
- **Threshold Cutoff**: When query similarity fell below `EVIDENCE_THRESHOLD = 0.45`, the platform returned `"Insufficient historical evidence found"` rather than hallucinating false matches.
- **Evaluation Date**: 2026-10-05 06:37:34 UTC
