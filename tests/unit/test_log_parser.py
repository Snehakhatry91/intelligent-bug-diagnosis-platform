"""
Unit Tests for Deterministic Log Parser
Validates deterministic extraction of exceptions, failure points, code paths,
and stack frames across Java, Python, Node, and Go.
"""

import pytest
from backend.services.log_parser_service import log_parser


def test_parse_java_null_pointer_trace():
    trace = """
    Exception in thread "main" java.lang.NullPointerException: Cannot read field "name"
        at com.example.service.UserService.getUserDetails(UserService.java:42)
        at com.example.web.UserController.handleRequest(UserController.java:18)
    """
    res = log_parser.parse(trace)
    assert res.exception_type == "java.lang.NullPointerException"
    assert "Cannot read field" in res.error_message
    assert len(res.stack_frames) == 2
    assert res.stack_frames[0].file == "UserService.java"
    assert res.stack_frames[0].line == 42
    assert "UserController.handleRequest" in res.stack_frames[1].function
    assert "NULL_POINTER_DEREFERENCE" in res.key_log_signals


def test_parse_python_traceback():
    trace = """
    Traceback (most recent call last):
      File "/app/backend/server.py", line 88, in process_transaction
        account.withdraw(amount)
      File "/app/backend/models.py", line 120, in withdraw
        raise ValueError("Insufficient balance")
    ValueError: Insufficient balance
    """
    res = log_parser.parse(trace)
    assert res.exception_type == "ValueError"
    assert "Insufficient balance" in res.error_message
    assert len(res.stack_frames) == 2
    assert res.stack_frames[1].file == "/app/backend/models.py"
    assert res.stack_frames[1].line == 120


def test_parse_node_javascript_error():
    trace = """
    TypeError: Cannot read properties of undefined (reading 'split')
        at parseToken (/usr/src/app/auth.js:45:22)
        at verifyRequest (/usr/src/app/middleware.js:12:9)
    """
    res = log_parser.parse(trace)
    assert res.exception_type == "TypeError"
    assert "Cannot read properties of undefined" in res.error_message
    assert len(res.stack_frames) == 2
    assert res.stack_frames[0].file == "/usr/src/app/auth.js"
    assert res.stack_frames[0].line == 45


def test_parse_system_signal():
    log_text = "2026-10-05 01:00:00 [Kernel] Process 4812 terminated with SIGSEGV (Segmentation fault) at address 0x00000000"
    res = log_parser.parse(log_text)
    assert res.exception_type == "SIGSEGV"
    assert "SIGSEGV" in res.key_log_signals


def test_parse_empty_content_returns_non_hallucinated_defaults():
    res = log_parser.parse("")
    assert res.exception_type is None
    assert res.failure_point is None
    assert res.stack_frames == []
    assert "Empty or null" in res.parsing_notes
