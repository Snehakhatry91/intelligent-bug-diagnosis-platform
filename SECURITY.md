# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the **Intelligent Bug Diagnosis Platform** seriously. If you discover a vulnerability, please report it responsibly:

1. **Do Not Open Public Issues:** Refrain from disclosing details in public GitHub issues, discussions, or pull requests.
2. **Contact Email:** Send an encrypted email with reproduction steps to `security@vidzai.internal` or via the project maintainers.
3. **Response Window:** Our engineering team acknowledges receipt within 48 hours and provides status updates every 5 business days until resolution.

## Platform Security Architecture

- **No Remote Code Execution:** Uploaded files (`.txt`, `.log`, `.md`, `.json`) are parsed strictly as plain text or structured JSON. Files are never compiled, invoked, executed, or passed to system shells.
- **Input Sanitization:** Multi-byte sequences, null bytes, and path traversal sequences (`../`, `..\\`) are stripped prior to storage.
- **Payload Limits:** Request bodies and file uploads are strictly limited to 5MB to mitigate memory exhaustion or Denial of Service (DoS).
- **Environment Isolation:** Secrets, database credentials, and optional LLM keys are accessed exclusively via environment variables (`.env`). No secrets are committed to the codebase.
- **Parameterized SQL:** All database interactions utilize SQLAlchemy ORM with bound parameters, preventing SQL injection.
- **CORS Protection:** Strict origin filtering prevents unauthorized cross-origin requests.
