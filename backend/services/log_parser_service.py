"""
Deterministic Log Parser Service
Extracts structured technical signals, stack traces, failure points, and exception details
from raw error logs and trace dumps without synthetic invention.
Supports Java, Python, JavaScript/Node, Go, and system log formats.
"""

import re
from typing import List, Optional
from backend.models.schemas import LogAnalysisResult, StackFrame


class DeterministicLogParser:
    """Robust, deterministic regex and structural parser for software crash logs."""

    # Python Traceback patterns
    PYTHON_TRACEBACK_START = re.compile(r"Traceback\s+\(most recent call last\):", re.IGNORECASE)
    PYTHON_FRAME = re.compile(r'File\s+"([^"]+)",\s+line\s+(\d+)(?:,\s+in\s+([^\n\r]+))?')
    PYTHON_EXCEPTION = re.compile(r"^\s*([a-zA-Z0-9_.]*(?:Error|Exception|Interrupt|Exit|Warning)):\s*(.*)$", re.MULTILINE)

    # Java Exception and Stack Trace patterns
    JAVA_EXCEPTION = re.compile(r"(?:Exception in thread \"[^\"]+\"\s+|(?:Caused by:\s+))?([a-zA-Z0-9_.$]+(?:Exception|Error|Throwable))(?::\s*([^\r\n]*))?")
    JAVA_FRAME = re.compile(r"^\s*at\s+([a-zA-Z0-9_.$]+)\.([a-zA-Z0-9_<>$]+)\(([^:)]+)(?::(\d+))?\)", re.MULTILINE)

    # JavaScript / Node.js patterns
    NODE_ERROR = re.compile(r"^\s*([a-zA-Z0-9_]*(?:Error|Exception|TypeError|ReferenceError|SyntaxError)):\s*(.*)$", re.MULTILINE)
    NODE_FRAME = re.compile(r"^\s*at\s+(?:([a-zA-Z0-9_.$<>]+)\s+)?\(?(?:file:\/\/)?([^:()]+):(\d+)(?::(\d+))?\)?", re.MULTILINE)

    # Go Panic patterns
    GO_PANIC = re.compile(r"^\s*panic:\s*(.*)", re.MULTILINE)
    GO_FRAME = re.compile(r"^\s*([^\s:]+\.[a-zA-Z0-9]+):(\d+)(?:\s+\+0x[0-9a-fA-F]+)?", re.MULTILINE)

    # System Signals
    SYSTEM_CRASH_PATTERNS = [
        ("SIGSEGV", re.compile(r"SIGSEGV|Segmentation\s+fault", re.IGNORECASE)),
        ("SIGKILL", re.compile(r"SIGKILL|Killed\s+process", re.IGNORECASE)),
        ("DeadlockDetected", re.compile(r"deadlock\s+detected|ResourceDeadlockException", re.IGNORECASE)),
        ("OutOfMemoryError", re.compile(r"OutOfMemoryError|memory\s+exhausted|Cannot\s+allocate\s+memory", re.IGNORECASE)),
        ("ConnectionRefused", re.compile(r"ConnectionRefusedError|ECONNREFUSED|Could\s+not\s+connect\s+to\s+server", re.IGNORECASE)),
        ("JWTExpired", re.compile(r"TokenExpiredError|ExpiredSignatureError|jwt\s+expired", re.IGNORECASE)),
        ("TimeoutError", re.compile(r"ETIMEDOUT|TimeoutError|Connection\s+timed\s+out|ReadTimeout", re.IGNORECASE)),
        ("QuotaExceeded", re.compile(r"QuotaExceededError|RateLimitError|429\s+Too\s+Many\s+Requests", re.IGNORECASE)),
    ]

    def parse(self, text: str) -> LogAnalysisResult:
        """Parse raw content deterministically into structured LogAnalysisResult."""
        if not text or not text.strip():
            return LogAnalysisResult(
                exception_type=None,
                error_message=None,
                failure_point=None,
                affected_code_path=None,
                key_log_signals=[],
                stack_frames=[],
                raw_extracted_facts=[],
                parsing_notes="Empty or null content provided."
            )

        key_signals = self._extract_key_signals(text)
        frames: List[StackFrame] = []
        exception_type: Optional[str] = None
        error_msg: Optional[str] = None
        failure_point: Optional[str] = None
        code_path: Optional[str] = None
        notes = []

        # 1. Check Python Traceback First
        if self.PYTHON_TRACEBACK_START.search(text) or ('File "' in text and "line " in text):
            notes.append("Detected Python traceback format")
            py_matches = list(self.PYTHON_FRAME.finditer(text))
            for m in py_matches:
                f_path = m.group(1).strip()
                line_no = int(m.group(2))
                fn = m.group(3).strip() if m.group(3) else None
                frames.append(StackFrame(
                    file=f_path,
                    line=line_no,
                    function=fn,
                    code_context=f"{f_path}:{line_no} in {fn}" if fn else f"{f_path}:{line_no}"
                ))

            py_ex = self.PYTHON_EXCEPTION.search(text)
            if py_ex:
                exception_type = py_ex.group(1).strip()
                error_msg = py_ex.group(2).strip()

        # 2. Check Java Stack Trace
        elif self.JAVA_FRAME.search(text):
            notes.append("Detected Java exception format")
            java_ex_match = self.JAVA_EXCEPTION.search(text)
            if java_ex_match:
                exception_type = java_ex_match.group(1).strip()
                error_msg = java_ex_match.group(2).strip() if java_ex_match.group(2) else ""

            for m in self.JAVA_FRAME.finditer(text):
                cls_name = m.group(1)
                method_name = m.group(2)
                file_name = m.group(3)
                line_no = int(m.group(4)) if m.group(4) else None
                frames.append(StackFrame(
                    file=file_name,
                    line=line_no,
                    function=f"{cls_name}.{method_name}",
                    code_context=f"{cls_name}.{method_name}({file_name}:{line_no})"
                ))

        # 3. Check JavaScript / Node.js
        elif self.NODE_FRAME.search(text) or ("TypeError:" in text or "ReferenceError:" in text or "SyntaxError:" in text or "Error:" in text):
            notes.append("Detected JavaScript/Node.js error format")
            node_match = self.NODE_ERROR.search(text)
            if node_match:
                exception_type = node_match.group(1).strip()
                error_msg = node_match.group(2).strip()

            for m in self.NODE_FRAME.finditer(text):
                fn = m.group(1) if m.group(1) else "anonymous"
                f_path = m.group(2).strip()
                line_no = int(m.group(3))
                frames.append(StackFrame(
                    file=f_path,
                    line=line_no,
                    function=fn,
                    code_context=f"{f_path}:{line_no}"
                ))

        # 4. Check Go Panic
        elif self.GO_PANIC.search(text):
            notes.append("Detected Go panic trace")
            go_panic = self.GO_PANIC.search(text)
            exception_type = "panic"
            error_msg = go_panic.group(1).strip()

            for m in self.GO_FRAME.finditer(text):
                f_path = m.group(1).strip()
                line_no = int(m.group(2))
                frames.append(StackFrame(
                    file=f_path,
                    line=line_no,
                    function=None,
                    code_context=f"{f_path}:{line_no}"
                ))

        # 5. Fallback System Signal detection if no structured exception
        if not exception_type:
            for sig_name, sig_regex in self.SYSTEM_CRASH_PATTERNS:
                if sig_regex.search(text):
                    exception_type = sig_name
                    error_msg = f"System signal {sig_name} detected in log stream."
                    notes.append(f"Identified system signal pattern: {sig_name}")
                    break

        # Derive failure point and affected code path from frames
        if frames:
            deepest_frame = frames[-1]
            failure_point = f"{deepest_frame.file}:{deepest_frame.line}" if deepest_frame.line else deepest_frame.file
            code_path = deepest_frame.function or deepest_frame.file
        else:
            path_match = re.search(r"([a-zA-Z0-9_\-./\\]+\.[a-zA-Z0-9]{1,5}):(\d+)", text)
            if path_match:
                failure_point = f"{path_match.group(1)}:{path_match.group(2)}"
                code_path = path_match.group(1)
            else:
                failure_point = "Information unavailable in submitted text."
                code_path = "Information unavailable."

        if not exception_type:
            exception_type = "UnknownError / UnstructuredLog"
            notes.append("No standard stack trace format matched; parsed as unstructured text.")

        if not error_msg:
            first_line = text.strip().split("\n")[0][:200]
            error_msg = first_line

        raw_facts = [
            f"Parsed exception signature: {exception_type}",
            f"Extracted error description: {error_msg}",
            f"Primary failure site: {failure_point}",
            f"Stack frame count extracted: {len(frames)}"
        ]
        if key_signals:
            raw_facts.append(f"Critical diagnostic signals: {', '.join(key_signals)}")

        return LogAnalysisResult(
            exception_type=exception_type,
            error_message=error_msg,
            failure_point=failure_point,
            affected_code_path=code_path,
            key_log_signals=key_signals,
            stack_frames=frames,
            raw_extracted_facts=raw_facts,
            parsing_notes="; ".join(notes) if notes else "Deterministic analysis completed."
        )

    def _extract_key_signals(self, text: str) -> List[str]:
        signals = []
        for name, pattern in self.SYSTEM_CRASH_PATTERNS:
            if pattern.search(text):
                signals.append(name)

        if "NullPointerException" in text:
            signals.append("NULL_POINTER_DEREFERENCE")
        if "timeout" in text.lower():
            signals.append("NETWORK_OR_IO_TIMEOUT")
        if "out of memory" in text.lower() or "heap space" in text.lower():
            signals.append("RESOURCE_EXHAUSTION_OOM")
        if "connection refused" in text.lower() or "connection reset" in text.lower():
            signals.append("DATABASE_OR_SOCKET_DISCONNECT")
        if "authentication" in text.lower() or "jwt" in text.lower() or "unauthorized" in text.lower():
            signals.append("SECURITY_AUTH_FAILURE")

        return list(dict.fromkeys(signals))


log_parser = DeterministicLogParser()
