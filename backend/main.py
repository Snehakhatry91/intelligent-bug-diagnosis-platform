"""
Main FastAPI Application Entrypoint
Configures CORS middleware, lifespan events, routes, and diagnostic health check endpoints.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db
from backend.api.submission import router as submission_router
from backend.api.diagnosis import router as diagnosis_router
from backend.api.historical import router as historical_router
from backend.api.analytics import router as analytics_router
from backend.api.knowledge_base import router as kb_router
from rag.vector_store import vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: Initialize DB tables and verify vector store on startup."""
    print("[Main] Initializing database schema...")
    await init_db()
    print("[Main] Loading vector store index...")
    vector_store.load()
    print(f"[Main] Ready. Vector index contains {vector_store.count()} chunks.")
    print("[Main] Pre-warming semantic embedder model...")
    from rag.embedder import embedder
    embedder.embed_text("startup-warmup")
    print("[Main] Semantic embedder pre-warmed successfully.")
    yield
    print("[Main] Shutting down application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Bug Diagnosis Platform with Multi-Agent Orchestration & RAG Fix Recommendations",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(submission_router, prefix="/api")
app.include_router(diagnosis_router, prefix="/api")
app.include_router(historical_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(kb_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint exposing system status, provider, and index size."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "vector_index_size": vector_store.count(),
        "similarity_policy": {
            "duplicate_threshold": settings.DUPLICATE_THRESHOLD,
            "related_threshold": settings.RELATED_THRESHOLD,
            "weak_threshold": settings.WEAK_THRESHOLD,
            "evidence_threshold": settings.EVIDENCE_THRESHOLD,
        }
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Intelligent Bug Diagnosis Platform API is operational.",
        "documentation": "/docs",
        "health": "/health"
    }
