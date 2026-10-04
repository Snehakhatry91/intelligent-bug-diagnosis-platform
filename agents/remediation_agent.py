"""
Remediation Agent
Generates concrete, actionable bug fix recommendations, implementation steps,
supporting evidence citations, and automated test specifications.
"""

from typing import Dict, List, Optional
from agents.base_agent import BaseAgent
from backend.models.schemas import (
    HistoricalEvidenceItem,
    LogAnalysisResult,
    RecommendedTest,
    RemediationRecommendation,
    RootCauseResult,
    SubmissionResponse,
    TriageResult,
)


class RemediationAgent(BaseAgent):
    """Produces engineering-grade code patches, implementation guidance, and test suites."""

    def __init__(self):
        super().__init__(
            name="Remediation Agent",
            description="Generates actionable code patches, implementation guidance, and automated test plans"
        )

    async def process(self, context_dict: Dict) -> RemediationRecommendation:
        """Derive concrete remediation based on diagnosed root cause and historical resolutions."""
        submission: SubmissionResponse = context_dict.get("submission")
        triage: Optional[TriageResult] = context_dict.get("triage")
        log_res: Optional[LogAnalysisResult] = context_dict.get("log_analysis")
        evidence: List[HistoricalEvidenceItem] = context_dict.get("rag_retrieval", [])
        root_cause: Optional[RootCauseResult] = context_dict.get("root_cause")

        ex_type = (log_res.exception_type if log_res and log_res.exception_type else "").lower()
        title_text = submission.title.lower()

        supporting_evidence = []
        if evidence:
            for item in evidence[:2]:
                if item.fix_patch_summary:
                    supporting_evidence.append(f"Precedent {item.issue_id}: {item.fix_patch_summary}")

        # Tailor specific code patches and test plans based on diagnosed failure mode
        if "nullpointer" in ex_type or "nullpointer" in title_text or "null" in title_text:
            action = "Add defensive null validation and safe dereferencing guards"
            explanation = "Prevents uncaught NullPointerException by validating state before invoking instance methods or properties."
            affected_area = log_res.affected_code_path if (log_res and log_res.affected_code_path) else "Component Reference Initialization"
            guidance = (
                "1. Guard the object dereference with an explicit `if (target != null)` check.\n"
                "2. If uninitialized, initialize with a safe default or return an explicit domain error.\n"
                "3. Ensure asynchronous lifecycle callbacks complete before invoking downstream handlers."
            )
            code_patch = (
                "// Defensive null guard\n"
                "if (targetObject == null) {\n"
                "    logger.warn(\"Target object is null; aborting or falling back to default\");\n"
                "    return Collections.emptyList();\n"
                "}\n"
                "return targetObject.execute();"
            )
            tests = [
                RecommendedTest(
                    test_type="Unit Test",
                    description="Verify that passing a null reference does not throw NullPointerException and handles gracefully.",
                    test_code_or_command="assertDoesNotThrow(() -> service.process(null));"
                ),
                RecommendedTest(
                    test_type="Regression Test",
                    description="Simulate asynchronous cancellation while request is in-flight."
                )
            ]

        elif "deadlock" in ex_type or "deadlock" in title_text or "pool" in title_text:
            action = "Implement bounded connection pool timeouts and unify lock acquisition order"
            explanation = "Resolves AB-BA resource deadlocks by standardizing lock order and bounding thread wait durations."
            affected_area = "Database Connection Pool / Concurrency Manager"
            guidance = (
                "1. Acquire locks in a globally strictly ordered sequence.\n"
                "2. Replace indefinite blocking synchronization with `tryLock(timeout, TimeUnit.SECONDS)`.\n"
                "3. Configure connection pool ceiling (maxPoolSize) and leak detection thresholds."
            )
            code_patch = (
                "// Non-blocking lock with timeout\n"
                "if (lock.tryLock(5, TimeUnit.SECONDS)) {\n"
                "    try {\n"
                "        performCriticalOperation();\n"
                "    } finally {\n"
                "        lock.unlock();\n"
                "    }\n"
                "} else {\n"
                "    throw new TimeoutException(\"Could not acquire lock within timeout period\");\n"
                "}"
            )
            tests = [
                RecommendedTest(
                    test_type="Stress / Concurrency Test",
                    description="Run 100 concurrent worker threads executing simultaneous read and write transactions."
                ),
                RecommendedTest(
                    test_type="Integration Test",
                    description="Assert database connection is returned to pool upon query completion."
                )
            ]

        elif "jwt" in ex_type or "auth" in title_text or "unauthorized" in title_text or "token" in title_text:
            action = "Normalize HTTP Authorization header lookup and handle token expiration lifecycle"
            explanation = "Standardizes case-insensitive header extraction and triggers graceful refresh upon token expiration."
            affected_area = "Security / Authentication Middleware"
            guidance = (
                "1. Inspect incoming headers using case-insensitive dictionary access.\n"
                "2. Catch TokenExpiredError and return 401 with `WWW-Authenticate: Bearer error=\"token_expired\"`.\n"
                "3. Configure client-side interceptor to auto-request token refresh before retrying."
            )
            code_patch = (
                "# Python / FastAPI Bearer Token normalization\n"
                "auth_header = request.headers.get('authorization') or request.headers.get('Authorization')\n"
                "if not auth_header or not auth_header.startswith('Bearer '):\n"
                "    raise HTTPException(status_code=401, detail='Missing or malformed Authorization header')\n"
                "token = auth_header.split(' ', 1)[1]"
            )
            tests = [
                RecommendedTest(
                    test_type="Unit Test",
                    description="Verify authentication succeeds when 'authorization' header is supplied in all-lowercase."
                ),
                RecommendedTest(
                    test_type="Integration Test",
                    description="Verify that an expired JWT token returns an explicit 401 with token_expired code."
                )
            ]

        elif "timeout" in ex_type or "timeout" in title_text or "socket" in title_text:
            action = "Implement retry with exponential backoff and bounded socket read timeouts"
            explanation = "Prevents client thread starvation caused by hanging remote endpoints."
            affected_area = "HTTP / Network Client Transport Layer"
            guidance = (
                "1. Configure connect timeout (5s) and read timeout (15s) explicitly.\n"
                "2. Wrap external calls in a retry policy with jittered exponential backoff.\n"
                "3. Ensure sockets and streams are closed in a finally block."
            )
            code_patch = (
                "// HTTP client timeout configuration\n"
                "RequestConfig config = RequestConfig.custom()\n"
                "    .setConnectTimeout(5000)\n"
                "    .setSocketTimeout(15000)\n"
                "    .setConnectionRequestTimeout(5000)\n"
                "    .build();"
            )
            tests = [
                RecommendedTest(
                    test_type="Integration Test",
                    description="Simulate an unresponsive mock server and verify socket disconnects after configured timeout."
                )
            ]

        elif "memory" in ex_type or "heap" in title_text or "outofmemory" in ex_type:
            action = "Switch from unbounded in-memory accumulation to paginated or streaming processing"
            explanation = "Eliminates heap exhaustion by bounding in-memory buffer size during large collection operations."
            affected_area = "Data Processing / Indexing Subsystem"
            guidance = (
                "1. Stream items using iterators/generators rather than materializing entire datasets in heap.\n"
                "2. Implement LRU cache eviction and explicit cleanup hooks.\n"
                "3. Configure JVM `-XX:+HeapDumpOnOutOfMemoryError` for proactive leak isolation."
            )
            code_patch = (
                "# Bounded batch stream processing\n"
                "def process_large_dataset(dataset, batch_size=1000):\n"
                "    for offset in range(0, len(dataset), batch_size):\n"
                "        batch = dataset[offset:offset + batch_size]\n"
                "        yield process_batch(batch)"
            )
            tests = [
                RecommendedTest(
                    test_type="Performance / Memory Test",
                    description="Process 1,000,000 records and assert peak resident memory stays below 512 MB."
                )
            ]

        else:
            action = "Apply defensive input validation and structured exception handling"
            explanation = "Ensures invalid states or unexpected input trigger clean error propagation rather than crashes."
            affected_area = triage.affected_component if triage else "Application Core"
            guidance = "Validate all input parameters against schema specifications before triggering execution."
            code_patch = (
                "try:\n"
                "    result = execute_operation(payload)\n"
                "except Exception as err:\n"
                "    logger.error(f'Operation failed gracefully: {err}', exc_info=True)\n"
                "    raise ServiceException('Operation could not be completed', original_error=err)"
            )
            tests = [
                RecommendedTest(
                    test_type="Unit Test",
                    description="Assert service handles malformed payloads with 422 Unprocessable Entity."
                )
            ]

        if not supporting_evidence:
            supporting_evidence.append("Aligned with standard enterprise software engineering failure mitigation patterns.")

        confidence = root_cause.confidence if root_cause else 0.82

        return RemediationRecommendation(
            action=action,
            explanation=explanation,
            affected_area=affected_area,
            implementation_guidance=guidance,
            supporting_evidence=supporting_evidence,
            confidence=round(confidence, 2),
            recommended_tests=tests,
            code_patch=code_patch
        )


remediation_agent = RemediationAgent()
