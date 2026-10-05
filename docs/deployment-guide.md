# Production Deployment Guide

## 1. Cloud & Container Architecture
The platform is designed for cloud-native deployment using Docker, Docker Compose, or modern serverless platforms.

### Production Docker Compose Configuration
The provided `docker-compose.yml` configures a complete three-tier architecture:
1. **Database Service**: PostgreSQL 16 (`pgvector/pgvector:pg16` image prepared for relational storage and production scaling migration)
2. **Backend Service**: FastAPI running under Uvicorn with Gunicorn process workers
3. **Frontend Service**: NGINX serving the optimized production React bundle and proxying `/api` requests

```bash
docker-compose up --build -d
```

---

## 2. Free-Tier Cloud Deployment Strategies

### A. Frontend on Vercel / Netlify
1. Connect GitHub repository to Vercel.
2. Set Root Directory to `frontend`.
3. Set Build Command: `npm run build`.
4. Set Output Directory: `dist`.
5. Configure Rewrites in `vercel.json`:
   ```json
   {
     "rewrites": [
       { "source": "/api/(.*)", "destination": "https://your-backend.onrender.com/api/$1" },
       { "source": "/health", "destination": "https://your-backend.onrender.com/health" },
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

### B. Backend on Render / Railway / Fly.io
1. Deploy as Python Web Service.
2. Build Command: `pip install -r requirements.txt && python scripts/ingest_historical_data.py`.
3. Start Command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
4. Environment Variables:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname` (or SQLite for minimal footprint)
   - `CORS_ORIGINS=["https://your-frontend.vercel.app"]`
   - `DUPLICATE_THRESHOLD=0.82`
   - `RELATED_THRESHOLD=0.65`
   - `EVIDENCE_THRESHOLD=0.45`

### C. Vector Store Architecture & Production Scaling Option
- **Current Evaluation Implementation:** The prototype uses a persistent local vector index (`rag/vector_index.pkl`) with NumPy-based cosine similarity for historical defect retrieval.
- **Production Scaling Option:** For enterprise-scale production deployment, the local index architecture can be migrated to a dedicated PostgreSQL database with `CREATE EXTENSION vector;` (e.g. Neon.tech, Supabase, or AWS RDS) or distributed vector engines (such as Qdrant).

---

## 3. Production Hardening & Security Checklist
- [x] Maximum file size set to 5 MB (`MAX_FILE_SIZE_BYTES=5242880`)
- [x] Allowed extensions strictly enforced (`.txt`, `.log`, `.md`, `.json`)
- [x] Null-byte stripping and control-character sanitization active
- [x] Zero uploaded-file execution guarantee (parsed purely as UTF-8 text streams)
- [x] Parameterized SQL statements via SQLAlchemy ORM (SQL-injection immune)
- [x] Strict CORS origin white-listing
- [x] Secrets segregated in environment variables; zero credentials in Git repository
