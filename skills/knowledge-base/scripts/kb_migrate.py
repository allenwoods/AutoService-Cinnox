#!/usr/bin/env python3
"""
Knowledge Base Migration Script (Phase 1A)

One-time migration to add domain/region/language/page_number columns to existing
kb_chunks table and backfill values from sources.json.

Safe to run multiple times (idempotent).

Usage:
    uv run skills/knowledge-base/scripts/kb_migrate.py
"""

import json
import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path.cwd()
KB_DIR = PROJECT_ROOT / ".autoservice" / "database" / "knowledge_base"
KB_DB = KB_DIR / "kb.db"
SOURCES_FILE = Path(__file__).parent.parent / "references" / "sources.json"


def main():
    print("[KB Migrate] Phase 1A: Add domain/region/language columns")
    print(f"  Database: {KB_DB}")

    if not KB_DB.exists():
        print("  ERROR: Database not found. Run kb_ingest.py first.")
        sys.exit(1)

    if not SOURCES_FILE.exists():
        print(f"  ERROR: sources.json not found at {SOURCES_FILE}")
        sys.exit(1)

    conn = sqlite3.connect(str(KB_DB))

    # Step 1: Add columns (safe if already exist)
    print("\n  Step 1: Adding columns...")
    for col_def in [
        "domain TEXT DEFAULT ''",
        "region TEXT DEFAULT ''",
        "language TEXT DEFAULT 'en'",
        "page_number INTEGER",
    ]:
        col_name = col_def.split()[0]
        try:
            conn.execute(f"ALTER TABLE kb_chunks ADD COLUMN {col_def}")
            print(f"    Added column: {col_name}")
        except sqlite3.OperationalError:
            print(f"    Column already exists: {col_name}")

    # Step 2: Create indexes
    print("\n  Step 2: Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kb_domain ON kb_chunks(domain)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kb_region ON kb_chunks(region)")
    print("    Created idx_kb_domain, idx_kb_region")
    conn.commit()

    # Step 3: Load source → domain/region mapping from sources.json
    print("\n  Step 3: Loading domain/region mapping from sources.json...")
    sources_data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))

    source_map: dict[str, dict] = {}
    for s in sources_data.get("files", []):
        source_map[s["id"]] = {
            "domain": s.get("domain", ""),
            "region": s.get("region", ""),
            "language": s.get("language", "en"),
        }
    for s in sources_data.get("web", []):
        source_map[s["id"]] = {
            "domain": s.get("domain", ""),
            "region": s.get("region", ""),
            "language": s.get("language", "en"),
        }

    print(f"    Loaded {len(source_map)} source mappings")
    for sid, meta in source_map.items():
        print(f"      {sid}: domain={meta['domain']}, region={meta['region']}")

    # Step 4: Update existing chunks
    print("\n  Step 4: Backfilling existing chunks...")
    total_updated = 0
    for source_id, meta in source_map.items():
        cursor = conn.execute(
            """UPDATE kb_chunks
               SET domain = ?, region = ?, language = ?
               WHERE source_id = ? AND (domain IS NULL OR domain = '')""",
            (meta["domain"], meta["region"], meta["language"], source_id),
        )
        if cursor.rowcount > 0:
            print(f"    {source_id}: updated {cursor.rowcount} chunks → domain={meta['domain']}")
            total_updated += cursor.rowcount

    conn.commit()

    # Step 5: Verify
    print(f"\n  Step 5: Verification")
    print(f"    Total chunks updated: {total_updated}")

    rows = conn.execute("""
        SELECT COALESCE(NULLIF(domain, ''), '(unset)') AS d, COUNT(*) AS cnt
        FROM kb_chunks GROUP BY d ORDER BY cnt DESC
    """).fetchall()
    print("    Domain distribution:")
    for domain_val, cnt in rows:
        print(f"      {domain_val}: {cnt} chunks")

    rows = conn.execute("""
        SELECT COALESCE(NULLIF(region, ''), '(unset)') AS r, COUNT(*) AS cnt
        FROM kb_chunks GROUP BY r ORDER BY cnt DESC
    """).fetchall()
    print("    Region distribution:")
    for region_val, cnt in rows:
        print(f"      {region_val}: {cnt} chunks")

    conn.close()
    print("\n[KB Migrate] Done.")


if __name__ == "__main__":
    main()
