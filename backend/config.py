"""
Application Configuration Module
Centralized configuration loaded from environment variables with strong type validation.
Single source of truth for all threshold policies, paths, and security constraints.
"""

from typing import List, Union
import json
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Workspace base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General App Config
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    APP_NAME: str = "Intelligent Bug Diagnosis Platform"
    APP_VERSION: str = "1.0.0"

    # Database Configuration
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'backend' / 'bug_diagnosis.db'}"

    # Semantic Vector & RAG Policy
    # Note: Exactly ONE similarity policy is defined and used system-wide
    VECTOR_DIMENSION: int = 384
    DUPLICATE_THRESHOLD: float = 0.82    # >= 0.82: Likely Duplicate
    RELATED_THRESHOLD: float = 0.65      # 0.65 - 0.81: Related Issue
    WEAK_THRESHOLD: float = 0.45         # 0.45 - 0.64: Weak Match
    EVIDENCE_THRESHOLD: float = 0.45     # Below 0.45: Insufficient historical evidence found

    VECTOR_INDEX_PATH: str = str(BASE_DIR / "rag" / "vector_index.pkl")
    KNOWLEDGE_BASE_DATA_DIR: str = str(BASE_DIR / "data")

    # LLM Provider Configuration
    # Options: "fallback" (deterministic heuristic engine), "ollama", "gemini", "openai"
    LLM_PROVIDER: str = "fallback"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Security & Input Constraints
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB maximum
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".log", ".md", ".json"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v


settings = Settings()
