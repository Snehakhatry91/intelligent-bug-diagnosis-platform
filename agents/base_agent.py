"""
Base Agent Abstract Class
Defines common execution lifecycle, timing telemetry, and safe error capture.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional, Tuple

from backend.models.schemas import TimelineStage

# Type alias for result and timeline telemetry pair
AgentTelemetryResult = Tuple[Any, TimelineStage]


class BaseAgent(ABC):
    """Abstract base class for all specialized diagnostic agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, context: Any) -> Any:
        """Core agent execution logic to be implemented by each specialized agent."""
        pass

    async def execute_with_telemetry(self, context: Any) -> AgentTelemetryResult:
        """Execute agent with precise millisecond duration measurement and exception safety."""
        start_time = time.perf_counter()
        timestamp = datetime.now(timezone.utc)
        status = "completed"

        try:
            result = await self.process(context)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stage = TimelineStage(
                stage_name=self.name,
                status=status,
                duration_ms=round(duration_ms, 2),
                timestamp=timestamp,
                notes=f"{self.description} completed in {duration_ms:.1f}ms"
            )
            return result, stage
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stage = TimelineStage(
                stage_name=self.name,
                status="failed",
                duration_ms=round(duration_ms, 2),
                timestamp=timestamp,
                notes=f"Error during {self.name}: {str(e)}"
            )
            return None, stage
