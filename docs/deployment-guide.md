# Cloud Deployment Guide

## 1. Deployment Overview & Architecture

> [!IMPORTANT]
> **Primary Demo & Evaluation Deployment:**
> - **Frontend:** [Vercel](https://vercel.com) (Static SPA hosting with API proxy rewrites)
> - **Backend:** [Render Web Service](https://render.com) (FastAPI application with dynamic `$PORT`)
> - **Current RAG Engine:** Persistent local vector index (`rag/vector_index.pkl`) with NumPy cosine similarity
> - **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions, local execution)
> - **LLM Provider:** Deterministic fallback heuristic engine (`LLM_PROVIDER=fallback`) by default
> - **Deployment Classification:** **Evaluation / Demo Deployment** (not enterprise persistent production)

The platform is designed to be deployed entirely on free cloud tiers without requiring external paid LLM/embedding API keys or locally managed Ollama daemon processes.

---

## 2. Backend Deployment on Render

The backend is deployed as a Render Web Service running Python. Render automatically discovers deployment parameters through the repository's root [`render.yaml`](file:///c:/Users/sneha/intelligent-bug-diagnosis-platform/render.yaml) blueprint.

### Service Configuration Summary
- **Entrypoint:** `backend.main:app`
- **Python Version:** `3.13` (enforced via [`.python-version`](file:///c:/Users/sneha/intelligent-bug-diagnosis-platform/.python-version) and `render.yaml`)
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python scripts/validate_historical_data.py && python scripts/ingest_historical_data.py
  ```
- **Start Command:**
  ```bash
  python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```
  *(Dynamic `$PORT` environment variable provided by Render is used; port 8000 is not hardcoded).*

### Environment Variables
Configure the following production defaults in Render (pre-configured in `render.yaml`):

| Variable | Value | Purpose |
|---|---|---|
| `ENVIRONMENT` | `production` | Production mode toggle |
| `DEBUG` | `False` | Disables debug logs and stack traces |
| `LLM_PROVIDER` | `fallback` | Deterministic offline reasoning engine (no Ollama required) |
| `VECTOR_DIMENSION` | `384` | Embedding dimensionality for `all-MiniLM-L6-v2` |
| `DUPLICATE_THRESHOLD` | `0.82` | Single source of truth threshold for duplicate detection |
| `RELATED_THRESHOLD` | `0.65` | Threshold for related defect classification |
| `WEAK_THRESHOLD` | `0.45` | Lower threshold for weak matches |
| `EVIDENCE_THRESHOLD` | `0.45` | Minimum retrieval score for fix synthesis evidence |
| `MAX_FILE_SIZE_BYTES` | `5242880` | 5 MB upload limit |
| `PYTHON_VERSION` | `3.13` | Explicit Python runtime version |

### Model Download & Build Ingestion Pipeline
During Render's build step:
1. `pip install -r requirements.txt` installs all framework, numerical, and machine-learning dependencies.
2. `python scripts/validate_historical_data.py` validates the 15-record historical defect dataset for source provenance and schema integrity.
3. `python scripts/ingest_historical_data.py` downloads and caches `sentence-transformers/all-MiniLM-L6-v2`, encodes all defect text chunks, creates `rag/vector_index.pkl`, and initializes the relational SQLite database `backend/bug_diagnosis.db`.
4. At runtime, `vector_store.load()` loads the pre-generated index in milliseconds without downloading external weights or hitting external APIs.

### Ephemeral Filesystem Limitation (Free Tier)
> [!WARNING]
> **Ephemeral Storage Notice:** Render's free tier uses an ephemeral filesystem. Any user-created bug submissions, diagnosis runs, or newly promoted knowledge base items created during runtime will reset when the free container spins down or restarts. The historical vector index and verified defect dataset are automatically rebuilt on each deployment build. This architecture is intentional and optimized for evaluation and demonstration.

---

## 3. Frontend Deployment on Vercel

The frontend is deployed as a single-page React/Vite application on Vercel.

### Vercel Project Settings
- **Framework Preset:** Vite
- **Root Directory:** `frontend`
- **Install Command:** `npm install`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### API Proxy & Rewrites Configuration
The frontend communicates via `const API_BASE = '/api';`. To route API requests seamlessly from the Vercel domain to the Render backend without cross-origin issues in the browser, rewrites are configured in [`frontend/vercel.json`](file:///c:/Users/sneha/intelligent-bug-diagnosis-platform/frontend/vercel.json):

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR_RENDER_BACKEND_URL.onrender.com/api/$1"
    },
    {
      "source": "/health",
      "destination": "https://YOUR_RENDER_BACKEND_URL.onrender.com/health"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

> [!NOTE]
> **Single Location for Backend URL:** Once your Render backend web service is deployed and has been assigned its URL (e.g., `https://intelligent-bug-diagnosis-backend.onrender.com`), update `YOUR_RENDER_BACKEND_URL.onrender.com` in `frontend/vercel.json` with that exact hostname.

---

## 4. CORS Whitelist Configuration

The backend enforces a strict CORS whitelist and disables wildcard credentials (`allow_origins=["*"]`).

- Requests proxied through Vercel's rewrite rules arrive at the backend from Vercel's edge, avoiding browser cross-origin blocking.
- For direct browser-to-backend requests, add your deployed Vercel domain to the `CORS_ORIGINS` environment variable in the Render Dashboard (or update `render.yaml`):
  ```env
  CORS_ORIGINS=http://localhost:5173,https://<your-vercel-domain>.vercel.app
  ```

---

## 5. Verification & Health Check Endpoints

Once deployed, verify the backend endpoints:
1. **System Health Check:**
   ```bash
   curl https://<your-render-service>.onrender.com/health
   ```
   Returns:
   ```json
   {
     "status": "healthy",
     "app": "Intelligent Bug Diagnosis Platform",
     "version": "1.0.0",
     "llm_provider": "fallback",
     "vector_index_size": 15,
     "similarity_policy": {
       "duplicate_threshold": 0.82,
       "related_threshold": 0.65,
       "weak_threshold": 0.45,
       "evidence_threshold": 0.45
     }
   }
   ```
2. **Interactive API Documentation:**
   Navigate to `https://<your-render-service>.onrender.com/docs` to view Swagger UI.

---

## 6. Vector Store Architecture & Enterprise Scaling Options

- **Current Evaluation Prototype:** The platform uses a persistent local vector index (`rag/vector_index.pkl`) serialized via Pickle with NumPy-accelerated cosine similarity calculation over 384-dimensional embeddings generated by `sentence-transformers/all-MiniLM-L6-v2`. It does **not** require PostgreSQL or pgvector to operate.
- **Future Enterprise Scaling:** For large-scale production deployments exceeding thousands of historical defect records, the vector architecture can be migrated to:
  - **pgvector:** PostgreSQL extension (`CREATE EXTENSION vector;`) hosted on managed databases (e.g., Supabase, Neon, or AWS RDS).
  - **Dedicated Vector Engines:** Distributed vector databases such as Qdrant, Milvus, or Pinecone.

---

## 7. Optional / Future Docker Compose Deployment

The root [`docker-compose.yml`](file:///c:/Users/sneha/intelligent-bug-diagnosis-platform/docker-compose.yml) file defines an optional three-tier architectural blueprint (PostgreSQL + pgvector container, backend service container, and frontend container). 

> [!NOTE]
> Docker Compose is provided as an optional / future containerization reference. Executing `docker-compose up` requires custom `backend/Dockerfile` and `frontend/Dockerfile` images to be authored. For the official evaluation and live demonstration, the **Vercel + Render** cloud deployment path is the primary target.
