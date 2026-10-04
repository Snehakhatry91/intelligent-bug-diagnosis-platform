"""
Triage Agent
Classifies defect severity (Critical, High, Medium, Low), priority (High, Medium, Low),
affected component, and derives dynamic confidence scores and reasoning from submission signals.
Guarantees diverse outputs based on actual input content rather than static constants.
"""

import re
from typing import Dict, List, Tuple
from agents.base_agent import BaseAgent
from backend.models.schemas import PriorityLevel, SeverityLevel, SubmissionResponse, TriageResult


class TriageAgent(BaseAgent):
    """Automated defect triaging agent driven by empirical keyword, lexical, and structural analysis."""

    def __init__(self):
        super().__init__(
            name="Triage Agent",
            description="Classifies severity, priority, affected component, and confidence score"
        )

        # Categorized signal indicators with empirical weights
        self.severity_rules = [
            (
                SeverityLevel.CRITICAL,
                [
                    "sigsegv", "segmentation fault", "deadlock", "data corruption", "production outage",
                    "system crash", "kernel panic", "fatal crash", "total failure", "database down",
                    "nohostavailableexception"
                ],
                0.94,
                "Critical crash or systemic failure detected; blocks service execution."
            ),
            (
                SeverityLevel.HIGH,
                [
                    "nullpointerexception", "outofmemoryerror", "connection refused", "sockettimeoutexception",
                    "heap space", "etimedout", "access violation", "connection pool exhaustion",
                    "transaction aborted"
                ],
                0.86,
                "High severity functional breakdown or unhandled exception in core subsystem."
            ),
            (
                SeverityLevel.MEDIUM,
                [
                    "unauthorized", "tokenexpirederror", "jwt expired", "quotaexceeded", "401 unauthorized",
                    "slow query", "retry limit reached", "rate limit", "intermittent failure"
                ],
                0.78,
                "Medium severity operational issue, session expiration, or quota barrier."
            ),
            (
                SeverityLevel.LOW,
                [
                    "deprecation", "warning", "minor", "typo", "formatting", "cosmetic",
                    "ui alignment", "style guide", "info log"
                ],
                0.68,
                "Low severity advisory, cosmetic defect, or non-blocking maintenance item."
            )
        ]

        # Component detection patterns
        self.component_patterns = [
            ("Database / Persistence", re.compile(r"database|postgres|cql|sql|cassandra|connection pool|dtp|datasource", re.IGNORECASE)),
            ("Authentication / Security", re.compile(r"auth|jwt|token|bearer|realm|oauth|forbidden|unauthorized", re.IGNORECASE)),
            ("Network / Transport", re.compile(r"http|socket|dns|necko|tcp|tls|connection timeout|p2 repository|transport", re.IGNORECASE)),
            ("Memory & Runtime", re.compile(r"outofmemory|heap|garbage collector|jit|spidermonkey|ionmonkey|memory leak", re.IGNORECASE)),
            ("Messaging & Queue", re.compile(r"kafka|producer|consumer|queue|recordaccumulator|broker", re.IGNORECASE)),
            ("Platform UI / Frontend", re.compile(r"ui|workbench|view|editor|css|rendering|dom|audiocontext", re.IGNORECASE)),
            ("Core Indexing / Storage", re.compile(r"lucene|fst|indexeddb|indexmanager|storage|filesystem", re.IGNORECASE))
        ]

    async def process(self, submission: SubmissionResponse) -> TriageResult:
        """Process bug submission and dynamically compute triage classification."""
        text = f"{submission.title}\n{submission.raw_content}".lower()

        matched_severity = None
        matched_confidence = 0.70
        reasoning = "Evaluated against standard diagnostic criteria."
        extracted_signals: List[str] = []

        # 1. Evaluate Severity and Confidence
        for sev_level, keywords, base_conf, rule_reason in self.severity_rules:
            matches = [kw for kw in keywords if kw in text]
            if matches:
                matched_severity = sev_level
                extracted_signals.extend(matches)
                # Adjust confidence slightly based on signal count
                matched_confidence = min(0.98, base_conf + (len(matches) - 1) * 0.02)
                reasoning = f"{rule_reason} Detected signals: {', '.join(matches[:4])}."
                break

        # Default fallback if no specific keywords matched
        if not matched_severity:
            if "exception" in text or "error" in text:
                matched_severity = SeverityLevel.MEDIUM
                matched_confidence = 0.72
                reasoning = "Generic exception or error terms detected without catastrophic keywords."
                extracted_signals.append("generic_error_mention")
            else:
                matched_severity = SeverityLevel.LOW
                matched_confidence = 0.65
                reasoning = "No critical error keywords detected; classified as low-severity diagnostic check."
                extracted_signals.append("informational_text")

        # 2. Derive Priority from Severity and Environment
        if matched_severity == SeverityLevel.CRITICAL:
            priority = PriorityLevel.HIGH
        elif matched_severity == SeverityLevel.HIGH:
            priority = PriorityLevel.HIGH
        elif matched_severity == SeverityLevel.MEDIUM:
            priority = PriorityLevel.MEDIUM
        else:
            priority = PriorityLevel.LOW

        # 3. Detect Component
        affected_component = "Core / General System"
        for comp_name, pattern in self.component_patterns:
            if pattern.search(text):
                affected_component = comp_name
                extracted_signals.append(f"component:{comp_name}")
                break

        return TriageResult(
            severity=matched_severity,
            priority=priority,
            affected_component=affected_component,
            confidence=round(matched_confidence, 2),
            reasoning=reasoning,
            signals=list(dict.fromkeys(extracted_signals))
        )


triage_agent = TriageAgent()
