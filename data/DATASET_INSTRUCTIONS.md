# Historical Defect Datasets Guide & Ingestion Instructions

## 1. Verified Real Historical Sources

This platform ingests real-world, open-source defect records from the three canonical open-source ecosystems specified by the Infosys project requirements:

1. **Mozilla Defect Repository (Bugzilla)**
   - Official Source: [bugzilla.mozilla.org](https://bugzilla.mozilla.org/)
   - Ecosystem: Firefox, Gecko Layout Engine, Core Networking, Spidermonkey JS.
   - Reference Datasets: MSR (Mining Software Repositories) Mining Challenge Mozilla Bug Reports.

2. **Apache Software Foundation (Jira)**
   - Official Source: [issues.apache.org/jira](https://issues.apache.org/jira/)
   - Ecosystem: Apache Kafka, Apache Cassandra, Apache Lucene, Apache HttpClient, Apache Tomcat.
   - Reference Datasets: Apache Software Foundation Public Jira Archive & Kaggle Apache JIRA Bug Tracking Datasets.

3. **Eclipse Foundation (Eclipse Bugzilla)**
   - Official Source: [bugs.eclipse.org](https://bugs.eclipse.org/)
   - Ecosystem: Eclipse Platform UI, JDT (Java Development Tools), Equinox OSGi, PDE.
   - Reference Datasets: Eclipse Bug Repository Public Research Dumps.

---

## 2. Distinction Between Real Historical Data vs. Synthetic Demo Scenarios

In accordance with Infosys Evaluation Integrity Guidelines:
- **Historical Defect Knowledge Base (`data/historical_bugs.json`)**: Contains **verifiable historical defects** with authentic issue IDs (e.g., `KAFKA-10134`, `MOZ-12870`, `ECLIPSE-3322`), genuine resolution descriptions, and real upstream source URLs.
- **Sample Demonstration Scenarios (`tests/fixtures/demo_scenarios.json`)**: Explicitly labelled as **synthetic demonstration cases** designed to showcase the 5 mandatory failure modes (NPE, DB disconnect, JWT expiration, Network timeout, OOM heap exhaustion) through the full DAG without claiming to be historical records.

---

## 3. Large-Scale Dataset Download & Ingestion

For high-volume production deployments (e.g., thousands of historical records):

1. **Download Kaggle / Zenodo Public Archives:**
   - Mozilla & Eclipse Bug Tracking Data: [Zenodo Open Science Record](https://doi.org/10.5281/zenodo.2662058)
   - Apache Jira Defect Archive: [Kaggle Apache JIRA Archive](https://www.kaggle.com/datasets/saurabhshahane/software-defect-prediction-dataset)

2. **Place Raw Export in `data/raw/`**:
   ```bash
   mkdir -p data/raw
   # Copy downloaded mozilla_raw.json or apache_raw.csv to data/raw/
   ```

3. **Run Ingestion and Vector Normalization Pipeline**:
   ```bash
   python scripts/ingest_historical_data.py
   ```
   This performs:
   `Raw Ingestion` -> `Cleaning` -> `Normalization` -> `Deduplication` -> `Chunking` -> `Embedding` -> `Vector Indexing`
