"""
LLM Provider Abstraction Layer
Supports local Ollama LLM integration and a transparent Deterministic Heuristic Fallback Engine.
Explicitly labels the fallback engine as deterministic rules rather than pretending to be an LLM.
"""

from abc import ABC, abstractmethod
import json
import os
import re
from typing import Any, Dict, Optional
import httpx

from backend.config import settings


class LLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response text from prompt."""
        pass

    @abstractmethod
    def provider_name(self) -> str:
        """Return transparent provider name and model descriptor."""
        pass


class DeterministicHeuristicEngine(LLMProvider):
    """
    Transparent Deterministic Heuristic Fallback Engine.
    Used for hermetic testing, offline environments, and verifiable evaluations.
    CRITICAL NOTICE: This is explicitly a deterministic rule and pattern reasoning engine, NOT an LLM.
    """

    def provider_name(self) -> str:
        return "Deterministic Heuristic Engine (Rule-based Fallback)"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Deterministic pattern-matching synthesis based on structured input signals."""
        lower_p = prompt.lower()

        # Synthesis response for root cause reasoning
        if "root cause" in lower_p or "hypothesis" in lower_p:
            if "nullpointerexception" in lower_p or "null pointer" in lower_p:
                return (
                    "Hypothesis: Unchecked dereference of uninitialized or null object reference in runtime execution thread.\n"
                    "Observed Facts: Stack trace confirms NullPointerException during method execution.\n"
                    "Inference: An asynchronous background task or callback modified or failed to populate the object instance prior to caller invocation."
                )
            elif "deadlock" in lower_p or "connection pool" in lower_p:
                return (
                    "Hypothesis: Resource contention and circular lock acquisition order across concurrent execution threads.\n"
                    "Observed Facts: Worker threads blocked waiting on saturated connection pool or mutual exclusion monitor.\n"
                    "Inference: Thread A acquired resource 1 and waited on resource 2 while Thread B held resource 2."
                )
            elif "jwt" in lower_p or "token" in lower_p or "auth" in lower_p:
                return (
                    "Hypothesis: Authentication token validation failure caused by expiration, signature mismatch, or header casing discrepancy.\n"
                    "Observed Facts: Client request rejected with 401 Unauthorized or expired token error.\n"
                    "Inference: Gateway or reverse proxy altered header casing or client clock drift triggered pre-mature token invalidation."
                )
            elif "timeout" in lower_p or "socket" in lower_p:
                return (
                    "Hypothesis: Network socket or upstream service read timeout under high latency or connection drop.\n"
                    "Observed Facts: Socket read operation halted exceeding configured timeout threshold.\n"
                    "Inference: Missing heartbeat or socket keep-alive caused reverse proxy connection drop."
                )
            elif "outofmemory" in lower_p or "heap" in lower_p:
                return (
                    "Hypothesis: Java virtual machine heap exhaustion caused by unbounded in-memory collection growth or memory leak.\n"
                    "Observed Facts: JVM aborted with OutOfMemoryError: Java heap space.\n"
                    "Inference: High-throughput ingestion or lack of LRU eviction buffer saturated old generation heap."
                )
            else:
                return (
                    "Hypothesis: Unhandled exception or unexpected component state during execution.\n"
                    "Observed Facts: Diagnostic logs recorded abnormal termination or error status.\n"
                    "Inference: Input parameters or system state violated component preconditions."
                )

        # Fallback generic completion
        return "Deterministic heuristic synthesis completed successfully."


class OllamaProvider(LLMProvider):
    """Local Ollama instance integration."""

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def provider_name(self) -> str:
        return f"Ollama Local LLM ({self.model})"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")


def get_llm_provider() -> LLMProvider:
    """Factory creating configured LLM provider with fallback guarantee."""
    provider_type = settings.LLM_PROVIDER.lower().strip()

    if provider_type == "ollama":
        try:
            return OllamaProvider()
        except Exception:
            print("[LLMProvider] Warning: Ollama init failed, defaulting to Deterministic Heuristic Engine.")
            return DeterministicHeuristicEngine()

    # Default to transparent Deterministic Heuristic Engine
    return DeterministicHeuristicEngine()


llm_client = get_llm_provider()
