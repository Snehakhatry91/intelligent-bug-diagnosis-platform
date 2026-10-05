# System Setup & Local Development Guide

## 1. System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.12 (Python 3.12.5 verified)
- **Node.js**: Version 18+ (Node v22.19.0 verified) & npm 10+
- **Database**: SQLite (default lightweight local engine); optional PostgreSQL 15+ for containerized production

---

## 2. Repository Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Snehakhatry91/intelligent-bug-diagnosis-platform.git
   cd intelligent-bug-diagnosis-platform
   ```

2. **Configure Environment Variables**:
   Copy the example environment configuration to `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 3. Data Validation, Ingestion & Vector Index Initialization

Before running the platform, validate dataset integrity, populate the historical defect database, and build the 384-dimensional dense semantic vector index:

1. **Validate Historical Data Integrity & Provenance**:
   ```bash
   python scripts/validate_historical_data.py
   ```

2. **Ingest Verified Records & Build Vector Index**:
   ```bash
   python scripts/ingest_historical_data.py
   ```
This pipeline performs:
1. Integrity and provenance validation across Mozilla, Apache, and Eclipse records
2. Schema creation and refresh in `backend/bug_diagnosis.db`
3. Semantic text chunking
4. 384-dimensional L2-normalized embedding generation using `sentence-transformers/all-MiniLM-L6-v2`
5. Vector index persistence to `rag/vector_index.pkl` with versioning metadata

---

## 4. Running the Platform Locally

### Terminal 1: Backend Server (FastAPI)
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### Terminal 2: Frontend Development Server (Vite React)
```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 5. Running Automated Test Suites & Benchmarks

1. **Execute Pytest Unit & Integration Suite**:
   ```bash
   python -m pytest tests -v
   ```
   Expected output: `25 passed`

2. **Execute Five Synthetic Demonstration Scenarios**:
   ```bash
   python scripts/run_demo_scenarios.py
   ```

3. **Execute Empirical Validation Benchmark**:
   ```bash
   python scripts/evaluate_agents.py
   ```

4. **Execute Single Reproducibility Verification Gate**:
   ```bash
   python scripts/verify_project.py
   ```
