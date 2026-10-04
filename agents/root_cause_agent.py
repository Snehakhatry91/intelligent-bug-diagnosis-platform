"""
Root Cause Agent
Synthesizes deterministic crash signals and RAG historical evidence to formulate
a root cause hypothesis with strict four-tier attribution:
1. OBSERVED FACTS (deterministic empirical data)
2. HISTORICAL EVIDENCE (retrieved historical precedents or 'Insufficient historical evidence')
3. AI INFERENCE (hypothesized failure chain clearly distinguished from fact)
4. FIX RECOMMENDATION (actionable remediation strategy)
"""

from typing import Dict, List, Optional
from agents.base_agent import BaseAgent
from agents.llm_provider import llm_client
from backend.config import settings
from backend.models.schemas import (
    BugAnalysisContext,
    HistoricalEvidenceItem,
    LogAnalysisResult,
    RootCauseResult,
    TriageResult,
)


class RootCauseAgent(BaseAgent):
    """Diagnoses underlying defect mechanisms while enforcing anti-hallucination guardrails."""

    def __init__(self):
        super().__init__(
            name="Root Cause Agent",
            description="Derives root cause hypothesis with four-tier attribution and anti-hallucination guardrails"
        )

    async def process(self, context_dict: Dict) -> RootCauseResult:
        """
        Process context containing submission, triage, log_analysis, and rag_retrieval.
        Returns RootCauseResult with clear attribution separation.
        """
        submission = context_dict.get("submission")
        triage: Optional[TriageResult] = context_dict.get("triage")
        log_res: Optional[LogAnalysisResult] = context_dict.get("log_analysis")
        evidence: List[HistoricalEvidenceItem] = context_dict.get("rag_retrieval", [])

        # 1. Gather OBSERVED FACTS (Deterministic, non-hallucinated)
        observed_facts: List[str] = []
        if log_res:
            observed_facts.extend(log_res.raw_extracted_facts)
            if log_res.failure_point and log_res.failure_point != "Information unavailable in submitted text.":
                observed_facts.append(f"Execution terminated at line/symbol: {log_res.failure_point}")
        if triage:
            observed_facts.append(f"Triage classified severity as {triage.severity.value} ({triage.affected_component})")

        if not observed_facts:
            observed_facts.append(f"Observed defect submission with title: '{submission.title}'")

        # 2. Gather HISTORICAL EVIDENCE (Anti-hallucination check)
        historical_evidence: List[str] = []
        if evidence:
            for item in evidence[:3]:
                historical_evidence.append(
                    f"Historical Match [{item.project} {item.issue_id}]: {item.title} "
                    f"(Similarity: {item.similarity_score * 100:.1f}%). Resolution: {item.fix_patch_summary or item.resolution}"
                )
            evidence_status = "sufficient"
        else:
            historical_evidence.append("Insufficient historical evidence found.")
            evidence_status = "insufficient"

        # 3. Derive AI INFERENCE & HYPOTHESIS
        # Construct synthesis prompt
        prompt = (
            f"Analyze the following software failure:\n"
            f"Title: {submission.title}\n"
            f"Component: {triage.affected_component if triage else 'General'}\n"
            f"Exception: {log_res.exception_type if log_res else 'None'}\n"
            f"Error Message: {log_res.error_message if log_res else 'None'}\n"
            f"Observed Facts: {'; '.join(observed_facts)}\n"
            f"Historical Evidence: {'; '.join(historical_evidence)}\n"
            f"Synthesize the root cause hypothesis and failure chain."
        )

        synthesis_text = await llm_client.generate(prompt)

        # Parse inference and hypothesis
        ai_inferences: List[str] = []
        hypothesis = ""

        lines = synthesis_text.strip().split("\n")
        for line in lines:
            if line.lower().startswith("hypothesis:"):
                hypothesis = line.split(":", 1)[1].strip()
            elif line.lower().startswith("inference:"):
                ai_inferences.append(line.split(":", 1)[1].strip())
            elif line.lower().startswith("observed facts:"):
                pass  # Keep our own deterministic observed facts
            elif line.strip():
                ai_inferences.append(line.strip())

        if not hypothesis:
            if evidence_status == "sufficient" and evidence:
                top_match = evidence[0]
                hypothesis = f"Historical evidence suggests alignment with [{top_match.project} {top_match.issue_id}]. Likely root cause: {log_res.exception_type or 'anomaly'} in {log_res.affected_code_path or (triage.affected_component if triage else 'subsystem')}."
            elif log_res and log_res.exception_type:
                hypothesis = f"Observed {log_res.exception_type}. Likely root cause: unhandled exception in {log_res.affected_code_path or 'system pipeline'}."
            else:
                hypothesis = f"Observed anomalous defect behavior in {triage.affected_component if triage else 'system'}. Likely state inconsistency."

        if not ai_inferences:
            ai_inferences.append("Derived from pattern matching against common architectural failure scenarios.")

        # Compute root cause confidence
        # Confidence is higher when grounded by historical evidence
        base_conf = triage.confidence if triage else 0.75
        if evidence_status == "sufficient":
            root_conf = min(0.96, base_conf + 0.05)
        else:
            root_conf = max(0.50, base_conf - 0.10)

        return RootCauseResult(
            hypothesis=hypothesis,
            confidence=round(root_conf, 2),
            observed_facts=observed_facts,
            historical_evidence=historical_evidence,
            ai_inference=ai_inferences,
            evidence_status=evidence_status
        )


root_cause_agent = RootCauseAgent()
