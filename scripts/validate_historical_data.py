#!/usr/bin/env python3
"""
Intelligent Bug Diagnosis Platform - Historical Defect Data Validation Script
Validates data integrity, provenance completeness, and authenticity of historical defects.
Exits with code 0 on success, code 1 on validation failure.
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse

# Force unbuffered stdout for reliable subprocess logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

REQUIRED_FIELDS = [
    "id",
    "project",
    "source",
    "source_issue_id",
    "source_url",
    "title",
    "description",
    "component",
    "resolution",
    "resolution_summary",
    "verified",
    "data_type"
]

VALID_SOURCES = {
    "Mozilla Bugzilla",
    "Apache Jira",
    "Eclipse Bugzilla"
}

VALID_URL_DOMAINS = {
    "bugzilla.mozilla.org",
    "issues.apache.org",
    "bugs.eclipse.org"
}

FORBIDDEN_PLACEHOLDERS = [
    "lorem ipsum",
    "todo",
    "tbd",
    "placeholder",
    "fake",
    "asdf",
    "test test"
]

def validate_record(record: dict, index: int) -> list[str]:
    errors = []
    rec_id = record.get("id", f"Record#{index}")

    # 1. Required fields present and non-empty
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"{rec_id}: missing required field '{field}'")
        elif record[field] is None:
            errors.append(f"{rec_id}: field '{field}' cannot be None")
        elif isinstance(record[field], str) and not record[field].strip():
            errors.append(f"{rec_id}: field '{field}' cannot be empty string")

    # 2. Verified flag must be boolean True
    if record.get("verified") is not True:
        errors.append(f"{rec_id}: 'verified' flag must be strictly True (got {record.get('verified')})")

    # 3. Data type must be "historical"
    if record.get("data_type") != "historical":
        errors.append(f"{rec_id}: 'data_type' must be 'historical' (got '{record.get('data_type')}')")

    # 4. Valid source
    source = record.get("source", "")
    if source not in VALID_SOURCES:
        errors.append(f"{rec_id}: invalid source '{source}', expected one of {VALID_SOURCES}")

    # 5. Valid URL
    url = record.get("source_url", "")
    parsed_url = urlparse(url)
    if not (parsed_url.scheme in ("http", "https") and parsed_url.netloc in VALID_URL_DOMAINS):
        errors.append(f"{rec_id}: invalid source_url '{url}', must belong to {VALID_URL_DOMAINS}")

    # 6. Title and description length & content
    title = str(record.get("title", "")).strip()
    if len(title) < 5:
        errors.append(f"{rec_id}: title too short ({len(title)} chars)")

    desc = str(record.get("description", "")).strip()
    if len(desc) < 15:
        errors.append(f"{rec_id}: description too short ({len(desc)} chars)")

    # 7. Check for forbidden placeholder text
    combined_text = f"{title} {desc} {record.get('resolution_summary', '')}".lower()
    for placeholder in FORBIDDEN_PLACEHOLDERS:
        if placeholder in combined_text:
            errors.append(f"{rec_id}: contains forbidden placeholder text '{placeholder}'")

    return errors

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    data_file = repo_root / "data" / "historical_bugs.json"

    print("==========================================")
    print("HISTORICAL DATA VALIDATION")
    print("==========================================")

    if not data_file.exists():
        print(f"Error: Historical dataset not found at {data_file}")
        print("Overall: FAIL")
        return 1

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception as exc:
        print(f"Error parsing {data_file}: {exc}")
        print("Overall: FAIL")
        return 1

    if not isinstance(records, list) or len(records) == 0:
        print("Error: Historical dataset must be a non-empty JSON array.")
        print("Overall: FAIL")
        return 1

    seen_ids = set()
    total_records = len(records)
    verified_records = 0
    invalid_records = 0
    all_errors = []

    for idx, rec in enumerate(records):
        rec_id = rec.get("id")
        if rec_id in seen_ids:
            all_errors.append(f"Duplicate issue ID detected: '{rec_id}'")
            invalid_records += 1
            continue
        seen_ids.add(rec_id)

        rec_errors = validate_record(rec, idx)
        if rec_errors:
            all_errors.extend(rec_errors)
            invalid_records += 1
        else:
            verified_records += 1

    print(f"Records checked:   {total_records}")
    print(f"Verified records:  {verified_records}")
    print(f"Invalid records:   {invalid_records}")

    if all_errors:
        print("\nValidation Errors Encountered:")
        for err in all_errors:
            print(f"  [ERROR] {err}")
        print("\nOverall: FAIL")
        return 1

    print("\nOverall: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
