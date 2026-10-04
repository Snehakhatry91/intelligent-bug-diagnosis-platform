"""
Historical Defect Ingestion & Vector Indexing Script
Executes full data pipeline:
Raw Ingestion -> Validation -> Deduplication -> Chunking -> SentenceTransformer Embedding -> Vector Indexing
Loads Mozilla, Apache, and Eclipse defects into database and builds persistent vector index.
Exits non-zero if validation or ingestion fails.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.database import AsyncSessionLocal, init_db
from backend.models.db_models import HistoricalDefect
from rag.text_chunker import text_chunker
from rag.embedder import embedder, EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, EMBEDDING_METRIC
from rag.vector_store import vector_store
from sqlalchemy import select, delete


REQUIRED_PROVENANCE_FIELDS = [
    "project", "source", "source_url", "title", "description",
    "component", "resolution", "fix_patch_summary"
]

VALID_PROJECTS = {"Mozilla", "Apache", "Eclipse"}


def validate_record_provenance(record: dict, record_idx: int, filename: str) -> None:
    """Validate that a historical record conforms to authentic provenance standards."""
    issue_id = record.get("issue_id") or record.get("id")
    if not issue_id:
        raise ValueError(f"[{filename} record #{record_idx}] Missing issue_id / id field.")

    for field in REQUIRED_PROVENANCE_FIELDS:
        val = record.get(field)
        if not val or not str(val).strip():
            raise ValueError(f"[{filename} {issue_id}] Missing required provenance field: '{field}'")

    project = record.get("project")
    if project not in VALID_PROJECTS:
        raise ValueError(f"[{filename} {issue_id}] Invalid project '{project}'. Must be one of {VALID_PROJECTS}")

    source_url = record.get("source_url", "")
    if not (source_url.startswith("https://") or source_url.startswith("http://")):
        raise ValueError(f"[{filename} {issue_id}] Invalid source_url: '{source_url}'. Must be a valid HTTP(S) URL.")

    if not record.get("verified", False):
        raise ValueError(f"[{filename} {issue_id}] Record must be verified (verified: true).")

    if record.get("data_type") != "historical":
        raise ValueError(f"[{filename} {issue_id}] Historical defect record must have data_type: 'historical'.")


async def run_ingestion():
    print("=" * 65)
    print("HISTORICAL DEFECT INGESTION & VECTOR INDEXING")
    print(f"Embedding Model:     {EMBEDDING_MODEL_NAME}")
    print(f"Embedding Dimension: {EMBEDDING_DIMENSION}")
    print(f"Similarity Metric:   {EMBEDDING_METRIC}")
    print("=" * 65)

    # 1. Initialize DB tables
    from sqlalchemy import text
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("DROP TABLE IF EXISTS historical_defects"))
            await session.commit()
        except Exception:
            pass
    await init_db()
    print("[1/5] Database schema initialized and refreshed.")

    # 2. Collect dataset files & validate provenance
    data_files = [
        BASE_DIR / "data" / "historical_bugs.json",
        BASE_DIR / "data" / "mozilla_bugs.json",
        BASE_DIR / "data" / "apache_bugs.json",
        BASE_DIR / "data" / "eclipse_bugs.json",
    ]

    all_records = {}
    total_loaded = 0

    for file_path in data_files:
        if not file_path.exists():
            print(f"[ERROR] Required dataset file missing: {file_path.name}")
            sys.exit(1)

        with open(file_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        for idx, r in enumerate(records):
            validate_record_provenance(r, idx, file_path.name)
            issue_id = r.get("issue_id") or r.get("id")
            if issue_id not in all_records:
                all_records[issue_id] = r
            total_loaded += 1

        print(f"[2/5] Verified provenance for {len(records)} records in {file_path.name}")

    print(f"      Total unique verified defects to index: {len(all_records)}")

    # 3. Clean and prepare database table
    async with AsyncSessionLocal() as session:
        # Clear existing historical records to avoid stale data
        await session.execute(delete(HistoricalDefect))
        await session.commit()

        for issue_id, record in all_records.items():
            db_record = HistoricalDefect(
                issue_id=record.get("issue_id") or record.get("id"),
                project=record["project"],
                source=record["source"],
                title=record["title"],
                description=record["description"],
                component=record["component"],
                severity=record.get("severity", "Medium"),
                priority=record.get("priority", "Medium"),
                status=record.get("status", "RESOLVED"),
                resolution=record["resolution"],
                fix_patch_summary=record.get("fix_patch_summary") or record.get("resolution_summary", ""),
                source_url=record["source_url"],
                verified=True,
                data_type="historical"
            )
            session.add(db_record)

        await session.commit()
    print(f"[3/5] Persisted {len(all_records)} verified defects to database.")

    # 4. Generate embeddings and populate vector store
    vector_store.clear()
    total_chunks = 0

    print("[4/5] Generating dense embeddings using SentenceTransformer...")
    for issue_id, record in all_records.items():
        chunks = text_chunker.chunk_defect_record(record)
        for chunk in chunks:
            vec = embedder.embed_text(chunk["text"])
            vector_store.add_document_chunk(chunk, vec)
            total_chunks += 1

    # 5. Persist vector store to disk
    vector_store.save()
    print(f"[5/5] Saved vector index to: {settings.VECTOR_INDEX_PATH}")
    print("=" * 65)
    print("INGESTION SUCCESS SUMMARY")
    print(f"Verified Defects Ingested: {len(all_records)}")
    print(f"Total Chunks Indexed:      {total_chunks}")
    print(f"Embedding Model:           {EMBEDDING_MODEL_NAME}")
    print(f"Embedding Dimension:       {EMBEDDING_DIMENSION}")
    print(f"Metric:                    {EMBEDDING_METRIC}")
    print("=" * 65)


if __name__ == "__main__":
    try:
        asyncio.run(run_ingestion())
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] Ingestion failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
