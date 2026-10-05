#!/usr/bin/env python3
"""
Single Comprehensive Reproducibility and Quality Gate Check
Validates all aspects of the Intelligent Bug Diagnosis Platform:
Step 1: Environment (Python 3.10+)
Step 2: Dependencies Availability
Step 3: Historical KB Data Integrity (Source Provenance & Curation)
Step 4: Embedding Model (all-MiniLM-L6-v2) & Dimension (384)
Step 5: Vector Index Compatibility & Versioning
Step 6: RAG Semantic Retrieval Test
Step 7: Automated Unit & Integration Tests (pytest)
Step 8: Agent & Multi-Agent DAG Evaluation
Step 9: Five Synthetic Demonstration Scenarios
Step 10: API Smoke & Contract Verification
Step 11: Frontend Production Bundle Build
Step 12: Final Quality Summary Gate
"""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

# Ensure immediate unbuffered output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def run_process(args, cwd=None):
    """Run process safely across operating systems without shell quoting hazards."""
    try:
        proc = subprocess.run(
            args,
            cwd=cwd or str(BASE_DIR),
            capture_output=True,
            text=True,
            shell=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


async def test_api_smoke():
    """Verify core FastAPI endpoints and response schema contracts."""
    from httpx import ASGITransport, AsyncClient
    from backend.main import app
    from backend.database import init_db

    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health endpoint
        r_health = await client.get("/health")
        if r_health.status_code != 200 or r_health.json().get("status") != "healthy":
            return False, f"/health returned status {r_health.status_code}"

        # 2. Historical defects endpoint
        r_hist = await client.get("/api/historical?limit=5")
        if r_hist.status_code != 200:
            return False, f"/api/historical returned status {r_hist.status_code}"
        hist_data = r_hist.json()
        if not isinstance(hist_data, list) or len(hist_data) == 0:
            return False, "Malformed /api/historical response structure, expected non-empty list"

        # 3. Analytics endpoint
        r_analytics = await client.get("/api/analytics")
        if r_analytics.status_code != 200:
            return False, f"/api/analytics returned status {r_analytics.status_code}"
        an_data = r_analytics.json()
        if "total_submissions" not in an_data or "reconciliation_verified" not in an_data:
            return False, "Malformed /api/analytics response structure"

        # 4. Verified Knowledge Base endpoint
        r_kb = await client.get("/api/knowledge-base")
        if r_kb.status_code != 200:
            return False, f"/api/knowledge-base returned status {r_kb.status_code}"

    return True, "API smoke test passed"


def main():
    print("=" * 65)
    print("INTELLIGENT BUG DIAGNOSIS PLATFORM — MASTER VERIFICATION GATE")
    print("=" * 65)

    status = {
        "Environment": "FAIL",
        "Dependencies": "FAIL",
        "Historical KB": "FAIL",
        "Embedding Model": "FAIL",
        "Vector Index": "FAIL",
        "RAG Retrieval": "FAIL",
        "Unit Tests": "FAIL",
        "Agent Evaluation": "FAIL",
        "Demo Scenarios": "FAIL",
        "API Verification": "FAIL",
        "Frontend Build": "FAIL",
    }

    # -------------------------------------------------------------
    # STEP 1: Python Environment
    # -------------------------------------------------------------
    print("\n[STEP 1/11] Validating Python Environment...")
    py_ver = sys.version_info
    print(f"  * Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver.major >= 3 and (py_ver.major > 3 or py_ver.minor >= 10):
        status["Environment"] = "PASS"
    else:
        print("  [ERROR] Python 3.10+ required.")
        return

    # -------------------------------------------------------------
    # STEP 2: Dependencies Availability
    # -------------------------------------------------------------
    print("\n[STEP 2/11] Validating Package Dependencies...")
    required_modules = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "aiosqlite", "numpy", "sentence_transformers", "torch", "pytest", "httpx"
    ]
    missing = []
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)

    if missing:
        print(f"  [ERROR] Missing required Python packages: {', '.join(missing)}")
        return
    print(f"  * Core Python packages verified: {', '.join(required_modules)}")
    status["Dependencies"] = "PASS"

    # -------------------------------------------------------------
    # STEP 3: Historical Dataset Validation
    # -------------------------------------------------------------
    print("\n[STEP 3/11] Validating Historical Dataset Integrity...")
    rc, out, err = run_process([sys.executable, "scripts/validate_historical_data.py"])
    print(f"  * {out.strip().splitlines()[-1] if out.strip() else err}")
    if rc == 0:
        status["Historical KB"] = "PASS"
    else:
        print(f"  [ERROR] Historical data validation failed:\n{err or out}")
        return

    # -------------------------------------------------------------
    # STEP 4: Embedding Model Verification
    # -------------------------------------------------------------
    print("\n[STEP 4/11] Validating Semantic Embedding Model...")
    try:
        from rag.embedder import embedder, EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION
        print(f"  * Model: {EMBEDDING_MODEL_NAME}")
        test_vec = embedder.embed_text("Deadlock between thread and pipe critical section")
        dim = len(test_vec)
        print(f"  * Output embedding dimension: {dim}")
        if dim == 384:
            status["Embedding Model"] = "PASS"
        else:
            print(f"  [ERROR] Expected dimension 384, got {dim}")
            return
    except Exception as e:
        print(f"  [ERROR] Embedding model failed to load: {e}")
        return

    # -------------------------------------------------------------
    # STEP 5: Vector Index & Ingestion Verification
    # -------------------------------------------------------------
    print("\n[STEP 5/11] Validating Vector Index...")
    from rag.vector_store import vector_store
    if not vector_store.is_ready():
        print("  * Vector index not ready. Ingesting historical data...")
        rc, out, err = run_process([sys.executable, "scripts/ingest_historical_data.py"])
        if rc != 0:
            print(f"  [ERROR] Ingestion failed:\n{err or out}")
            return
        vector_store.load()

    cnt = vector_store.count()
    print(f"  * Vector index loaded with {cnt} chunks.")
    if cnt >= 15:
        status["Vector Index"] = "PASS"
    else:
        print(f"  [ERROR] Expected at least 15 indexed chunks, found {cnt}.")
        return

    # -------------------------------------------------------------
    # STEP 6: RAG Semantic Retrieval Test
    # -------------------------------------------------------------
    print("\n[STEP 6/11] Testing RAG Semantic Retrieval Engine...")
    from rag.retrieval_engine import retrieval_engine
    ev_items, msg = retrieval_engine.retrieve_evidence("Deadlock between thread and pipe lock", top_k=2)
    if ev_items:
        top_match = ev_items[0]
        print(f"  * Retrieved {len(ev_items)} match(es). Top: {top_match.issue_id} ({top_match.similarity_score * 100:.1f}%)")
        status["RAG Retrieval"] = "PASS"
    else:
        print(f"  [ERROR] Retrieval test returned no results: {msg}")
        return

    # -------------------------------------------------------------
    # STEP 7: Automated Unit & Integration Tests
    # -------------------------------------------------------------
    print("\n[STEP 7/11] Running pytest Suite...")
    rc, out, err = run_process([sys.executable, "-m", "pytest", "tests", "-q"])
    print(f"  * Output: {out.strip().splitlines()[-1] if out.strip() else err}")
    if rc == 0:
        status["Unit Tests"] = "PASS"
    else:
        print(f"  [ERROR] pytest failed:\n{err or out}")
        return

    # -------------------------------------------------------------
    # STEP 8: Agent & Benchmark Evaluation
    # -------------------------------------------------------------
    print("\n[STEP 8/11] Running Agent Benchmark Evaluation...")
    rc, out, err = run_process([sys.executable, "scripts/evaluate_agents.py"])
    if rc == 0:
        eval_json = BASE_DIR / "reports" / "latest_evaluation.json"
        if eval_json.exists():
            with open(eval_json, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            print(f"  * Severity Accuracy:  {metrics.get('severity_accuracy', 0)*100:.1f}%")
            print(f"  * Priority Accuracy:  {metrics.get('priority_accuracy', 0)*100:.1f}%")
            print(f"  * Duplicate Accuracy: {metrics.get('duplicate_accuracy', 0)*100:.1f}%")
            print(f"  * Duplicate F1-Score: {metrics.get('duplicate_f1', 0)*100:.1f}%")
        status["Agent Evaluation"] = "PASS"
    else:
        print(f"  [ERROR] evaluate_agents.py failed:\n{err or out}")
        return

    # -------------------------------------------------------------
    # STEP 9: Five Demo Scenarios
    # -------------------------------------------------------------
    print("\n[STEP 9/11] Running Five Synthetic Demo Scenarios...")
    rc, out, err = run_process([sys.executable, "scripts/run_demo_scenarios.py"])
    if rc == 0:
        print("  * All 5 synthetic demo scenarios executed end-to-end successfully.")
        status["Demo Scenarios"] = "PASS"
    else:
        print(f"  [ERROR] run_demo_scenarios.py failed:\n{err or out}")
        return

    # -------------------------------------------------------------
    # STEP 10: API Smoke & Contract Verification
    # -------------------------------------------------------------
    print("\n[STEP 10/11] Running API Smoke Verification...")
    try:
        api_ok, api_msg = asyncio.run(test_api_smoke())
        if api_ok:
            print("  * Core API endpoints (/health, /api/historical, /api/analytics, /api/knowledge-base) verified.")
            status["API Verification"] = "PASS"
        else:
            print(f"  [ERROR] API verification failed: {api_msg}")
            return
    except Exception as e:
        print(f"  [ERROR] API smoke test encountered exception: {e}")
        return

    # -------------------------------------------------------------
    # STEP 11: Frontend Production Build
    # -------------------------------------------------------------
    print("\n[STEP 11/11] Running Frontend Production Build (npm run build)...")
    frontend_dir = BASE_DIR / "frontend"
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    rc, out, err = run_process([npm_cmd, "run", "build"], cwd=str(frontend_dir))
    if rc == 0:
        print("  * Frontend built successfully (dist/ bundle created).")
        status["Frontend Build"] = "PASS"
    else:
        print(f"  [ERROR] Frontend build failed:\n{err or out}")
        return

    # -------------------------------------------------------------
    # STEP 12: Final Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 35)
    print("PROJECT VERIFICATION")
    print("=" * 35)
    all_passed = True
    for item, res in status.items():
        print(f"{item:<18}: {res}")
        if res != "PASS":
            all_passed = False

    print("-" * 35)
    overall = "PASS" if all_passed else "FAIL"
    print(f"Overall           : {overall}")
    print("=" * 35)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
