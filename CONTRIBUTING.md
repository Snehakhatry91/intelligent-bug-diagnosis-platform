# Contributing Guidelines

Thank you for your interest in contributing to the **Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance**!

## Development Workflow
1. **Fork and Clone** the repository.
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Environment Setup**:
   Follow instructions in [docs/setup-guide.md](docs/setup-guide.md).
   ```bash
   pip install -r requirements.txt
   python scripts/ingest_historical_data.py
   cd frontend && npm install && cd ..
   ```
4. **Code Standards**:
   - Python code must conform to PEP 8.
   - All datetime timestamps must use `datetime.now(timezone.utc)`.
   - Never hardcode similarity thresholds in individual files; import from `backend/config.py`.
   - All analytics queries must maintain strict mathematical reconciliation ($\sum \text{Counts} \equiv \text{Population}$).
5. **Testing**:
   Run the full test suite and ensure 100% pass rate:
   ```bash
   python -m pytest tests -v
   cd frontend && npm run build
   ```
6. **Submit a Pull Request**:
   Fill in the provided PR template and link any relevant User Story IDs.
