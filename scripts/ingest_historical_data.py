"""
Historical Defect Ingestion & Vector Indexing Script
Executes full data pipeline:
Raw Ingestion -> Cleaning -> Normalization -> Deduplication -> Chunking -> Embedding -> Vector Indexing
Loads Mozilla, Apache, and Eclipse defects into PostgreSQL/SQLite and builds persistent vector index.
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
from rag.embedder import embedder
from rag.vector_store import vector_store
from sqlalchemy import select


async def run_ingestion():
    print("=" * 60)
    print("STARTING HISTORICAL DEFECT INGESTION & VECTOR INDEXING")
    print("=" * 60)

    # 1. Initialize DB tables
    await init_db()
    print("[OK] Initialized database schema")

    # 2. Collect dataset files
    data_files = [
        BASE_DIR / "data" / "historical_bugs.json",
        BASE_DIR / "data" / "mozilla_bugs.json",
        BASE_DIR / "data" / "apache_bugs.json",
        BASE_DIR / "data" / "eclipse_bugs.json",
    ]

    all_records = {}
    for file_path in data_files:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for r in records:
                    issue_id = r.get("issue_id")
                    if issue_id and issue_id not in all_records:
                        all_records[issue_id] = r
            print(f"[OK] Loaded {len(records)} records from {file_path.name}")
        else:
            print(f"[WARN] File not found: {file_path.name}")

    print(f"\nTotal unique historical defect records to ingest: {len(all_records)}")

    # 3. Ingest records into Database and Vector Store
    vector_store.clear()
    total_chunks = 0

    async with AsyncSessionLocal() as session:
        for issue_id, record in all_records.items():
            # Check if exists in DB
            q = select(HistoricalDefect).where(HistoricalDefect.issue_id == issue_id)
            existing = (await session.execute(q)).scalar_one_or_none()

            if not existing:
                db_record = HistoricalDefect(
                    issue_id=record["issue_id"],
                    project=record["project"],
                    source=record["source"],
                    title=record["title"],
                    description=record["description"],
                    component=record["component"],
                    severity=record["severity"],
                    priority=record["priority"],
                    status=record["status"],
                    resolution=record["resolution"],
                    fix_patch_summary=record["fix_patch_summary"],
                    source_url=record["source_url"]
                )
                session.add(db_record)

            # Chunk record
            chunks = text_chunker.chunk_defect_record(record)
            for chunk in chunks:
                vec = embedder.embed_text(chunk["text"])
                vector_store.add_document_chunk(chunk, vec)
                total_chunks += 1

        await session.commit()
        print(f"[OK] Persisted {len(all_records)} historical defects to database")

    # 4. Save Vector Store Index
    vector_store.save()
    print(f"[OK] Built and saved vector index to {settings.VECTOR_INDEX_PATH}")
    print(f"[OK] Indexed chunks: {total_chunks} across {len(all_records)} unique defects")
    print(f"[OK] Embedding vector dimension: {settings.VECTOR_DIMENSION}")
    print("=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_ingestion())
