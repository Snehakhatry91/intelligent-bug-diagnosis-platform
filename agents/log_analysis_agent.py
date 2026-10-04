"""
Log Analysis Agent
Executes structured deterministic parsing on submission logs and stack traces.
Extracts exception signatures, failure points, code paths, and stack frames
without inventing synthetic details.
"""

from agents.base_agent import BaseAgent
from backend.models.schemas import LogAnalysisResult, SubmissionResponse
from backend.services.log_parser_service import log_parser


class LogAnalysisAgent(BaseAgent):
    """Deterministic structural and semantic log analysis agent."""

    def __init__(self):
        super().__init__(
            name="Log Analysis Agent",
            description="Parses stack traces, extracts failure points, code paths, and diagnostic signals"
        )

    async def process(self, submission: SubmissionResponse) -> LogAnalysisResult:
        """Analyze raw content and produce structured log diagnostics."""
        result = log_parser.parse(submission.raw_content)
        return result


log_analysis_agent = LogAnalysisAgent()
