"""
Single Comprehensive Reproducibility and Quality Gate Check
Validates all aspects of the Intelligent Bug Diagnosis Platform:
Step 1: Environment (Python, Packages, Frontend)
Step 2: Historical Dataset Provenance & Data Integrity
Step 3: RAG (SentenceTransformer, 384 dimensions, Vector Index, Retrieval)
Step 4: Automated Unit & Integration Tests (pytest)
Step 5: Agent & Multi-Agent DAG Evaluation
Step 6: Five Synthetic Demonstration Scenarios
Step 7: Frontend Production Bundle Build
Step 8: Final Summary Gate
"""

import json
import os
from pathlib import Path
import shutil
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


def main():
    print("=" * 65)
    print("INTELLIGENT BUG DIAGNOSIS PLATFORM — REPRODUCIBILITY VERIFICATION")
    print("=" * 65)

    status = {
        "Historical KB": "FAIL",
        "Embedding Model": "FAIL",
        "Vector Index": "FAIL",
        "Unit Tests": "FAIL",
        "Agent Evaluation": "FAIL",
        "Demo Scenarios": "FAIL",
        "Frontend Build": "FAIL",
    }

    # -------------------------------------------------------------
    # STEP 1: Environment Validation
    # -------------------------------------------------------------
    print("\n[STEP 1/8] Validating Environment...")
    py_ver = sys.version_info
    print(f"  * Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 10):
        print("  [ERROR] Python 3.10+ required.")
        return

    required_modules = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "aiosqlite", "numpy", "sentence_transformers", "torch", "pytest"
    ]
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            print(f"  [ERROR] Missing required Python package: {mod}")
            return
    print(f"  * Core Python modules verified: {', '.join(required_modules)}")

    frontend_dir = BASE_DIR / "frontend"
    if not (frontend_dir / "node_modules").exists():
        print("  [ERROR] Frontend node_modules not found. Run: cd frontend && npm install")
        return
    print("  * Frontend node_modules present.")

    # -------------------------------------------------------------
    # STEP 2: Historical Dataset Validation
    # -------------------------------------------------------------
    print("\n[STEP 2/8] Validating Historical Dataset Integrity...")
    data_dir = BASE_DIR / "data"
    hist_file = data_dir / "historical_bugs.json"
    if not hist_file.exists():
        print("  [ERROR] data/historical_bugs.json missing.")
        return

    with open(hist_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"  * Records found: {len(records)}")
    if len(records) < 15:
        print(f"  [ERROR] Insufficient records ({len(records)} < 15).")
        return

    seen_ids = set()
    required_fields = ["project", "source", "source_url", "title", "description", "component", "resolution", "fix_patch_summary"]
    for idx, r in enumerate(records):
        cid = r.get("issue_id") or r.get("id")
        if not cid or cid in seen_ids:
            print(f"  [ERROR] Invalid or duplicate issue_id: {cid}")
            return
        seen_ids.add(cid)

        for f_name in required_fields:
            if not r.get(f_name):
                print(f"  [ERROR] Record {cid} missing field: {f_name}")
                return

        if not r.get("verified", False):
            print(f"  [ERROR] Record {cid} verified flag is not True.")
            return

        if r.get("data_type") != "historical":
            print(f"  [ERROR] Record {cid} data_type is not 'historical'.")
            return

        if not r.get("source_url", "").startswith("http"):
            print(f"  [ERROR] Record {cid} has invalid source_url: {r.get('source_url')}")
            return

    print("  * All records verified for authentic provenance, verified=True, and valid URLs.")
    status["Historical KB"] = "PASS"

    # -------------------------------------------------------------
    # STEP 3: RAG (Embedding Model & Vector Index)
    # -------------------------------------------------------------
    print("\n[STEP 3/8] Validating RAG & Semantic Vector Index...")
    try:
        from rag.embedder import embedder, EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION
        print(f"  * Loading embedding model: {EMBEDDING_MODEL_NAME}")
        test_vec = embedder.embed_text("Test defect embedding for vector verification")
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

    from rag.vector_store import vector_store
    if not vector_store.is_ready():
        print("  * Vector index not ready. Ingesting historical data...")
        rc, out, err = run_process([sys.executable, "scripts/ingest_historical_data.py"])
        if rc != 0:
            print(f"  [ERROR] Ingestion script failed:\n{err or out}")
            return
        vector_store.load()

    cnt = vector_store.count()
    print(f"  * Vector index loaded with {cnt} chunks.")
    if cnt > 0:
        from rag.retrieval_engine import retrieval_engine
        ev_items, msg = retrieval_engine.retrieve_evidence("Deadlock between thread and pipe lock", top_k=2)
        if ev_items:
            print(f"  * Retrieval test returned {len(ev_items)} matches. Top match: {ev_items[0].issue_id} ({ev_items[0].similarity_score * 100:.1f}%)")
            status["Vector Index"] = "PASS"
        else:
            print(f"  [ERROR] Retrieval test returned no results: {msg}")
    else:
        print("  [ERROR] Vector index has 0 chunks.")

    # -------------------------------------------------------------
    # STEP 4: Automated Unit & Integration Tests
    # -------------------------------------------------------------
    print("\n[STEP 4/8] Running pytest Suite...")
    rc, out, err = run_process([sys.executable, "-m", "pytest", "tests", "-q"])
    print(f"  * Output: {out.strip()}")
    if rc == 0:
        status["Unit Tests"] = "PASS"
    else:
        print(f"  [ERROR] pytest failed:\n{err or out}")

    # -------------------------------------------------------------
    # STEP 5: Agent & Multi-Agent Evaluation
    # -------------------------------------------------------------
    print("\n[STEP 5/8] Running Agent Benchmark Evaluation...")
    rc, out, err = run_process([sys.executable, "scripts/evaluate_agents.py"])
    if rc == 0:
        print("  * Evaluation completed successfully.")
        # Load and print summary
        eval_json = BASE_DIR / "reports" / "latest_evaluation.json"
        if eval_json.exists():
            with open(eval_json, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            print(f"    - Severity Accuracy:  {metrics.get('severity_accuracy', 0)*100:.1f}%")
            print(f"    - Priority Accuracy:  {metrics.get('priority_accuracy', 0)*100:.1f}%")
            print(f"    - Duplicate Accuracy: {metrics.get('duplicate_accuracy', 0)*100:.1f}%")
            print(f"    - Duplicate F1-Score: {metrics.get('duplicate_f1', 0)*100:.1f}%")
        status["Agent Evaluation"] = "PASS"
    else:
        print(f"  [ERROR] evaluate_agents.py failed:\n{err or out}")

    # -------------------------------------------------------------
    # STEP 6: Demo Scenarios
    # -------------------------------------------------------------
    print("\n[STEP 6/8] Running Five Synthetic Demo Scenarios...")
    rc, out, err = run_process([sys.executable, "scripts/run_demo_scenarios.py"])
    if rc == 0:
        print("  * All 5 synthetic demo scenarios executed end-to-end successfully.")
        status["Demo Scenarios"] = "PASS"
    else:
        print(f"  [ERROR] run_demo_scenarios.py failed:\n{err or out}")

    # -------------------------------------------------------------
    # STEP 7: Frontend Production Build
    # -------------------------------------------------------------
    print("\n[STEP 7/8] Running Frontend Production Build (npm run build)...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    rc, out, err = run_process([npm_cmd, "run", "build"], cwd=str(frontend_dir))
    if rc == 0:
        print("  * Frontend built successfully (dist/ bundle created).")
        status["Frontend Build"] = "PASS"
    else:
        print(f"  [ERROR] Frontend build failed:\n{err or out}")

    # -------------------------------------------------------------
    # STEP 8: Final Summary Table
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
