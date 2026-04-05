#!/usr/bin/env python3
"""
Build glossary.json and synonym-map.json from a glossary CSV.

Usage:
    uv run skills/knowledge-base/scripts/build_glossary.py
    uv run skills/knowledge-base/scripts/build_glossary.py --csv docs/resource/other.csv
    uv run skills/knowledge-base/scripts/build_glossary.py --out-dir /custom/output/
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# Defaults
DEFAULT_CSV = Path("docs/resource/glossary.csv")
DEFAULT_OUT_DIR = Path("skills/sales-demo/references")


def load_csv(csv_path: Path) -> list[dict]:
    """Load glossary CSV, return list of rows."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "term": row.get("Glossary-EN", "").strip(),
                "description": row.get("Description", "").strip(),
                "related": row.get("Related Glossary", "").strip(),
            })
    return [r for r in rows if r["term"]]


def build_glossary(rows: list[dict]) -> dict:
    """Build glossary.json: { term: { description, related } }."""
    glossary = {}
    for row in rows:
        related = [r.strip() for r in row["related"].split(",") if r.strip()] if row["related"] else []
        glossary[row["term"]] = {
            "description": row["description"],
            "related": related,
        }
    return glossary


def build_synonym_map(rows: list[dict], glossary: dict) -> dict:
    """
    Build synonym-map.json: { colloquial_or_abbrev: official_term }.

    Sources:
    1. "See: XXX" pattern in description
    2. Parenthetical abbreviations: "Active Directory (AD)" → AD → Active Directory (AD)
    3. "Stands for XXX" pattern
    4. "Also known as XXX" pattern
    5. Common abbreviation in term itself (e.g. PSTN, DID, IDD)
    """
    synonyms: dict[str, str] = {}

    for row in rows:
        term = row["term"]
        desc = row["description"]

        # 1. "See: XXX"
        m = re.match(r"^See:\s*(.+)$", desc, re.IGNORECASE)
        if m:
            target = m.group(1).strip().rstrip(".")
            if target in glossary:
                synonyms[term.lower()] = target

        # 2. Parenthetical abbreviations: "Active Directory (AD)" → AD maps to full term
        m = re.match(r"^(.+?)\s*\(([A-Z]{2,})\)\s*$", term)
        if m:
            full_name = m.group(1).strip()
            abbrev = m.group(2)
            synonyms[abbrev.lower()] = term
            if full_name.lower() != term.lower():
                synonyms[full_name.lower()] = term

        # 3. Reverse: terms that ARE abbreviations with full form in parens
        # e.g. "PSTN (Public Switched Telephone Network)"
        # Use greedy match and strip to handle trailing spaces inside parens
        m = re.match(r"^([A-Z]{2,})\s*\((.+)\)\s*$", term)
        if m:
            abbrev = m.group(1)
            full_name = m.group(2).strip()
            synonyms[full_name.lower()] = term
            synonyms[abbrev.lower()] = term

        # 4. "Stands for XXX" in description
        m = re.match(r"^Stands for\s+(.+?)\.\s", desc)
        if m:
            expanded = m.group(1).strip()
            if expanded.lower() != term.lower():
                synonyms[expanded.lower()] = term

        # 5. "Also known as XXX" in description — capture until sentence boundary
        m = re.search(r"also known as\s+([A-Za-z][\w\s\-]+?)[\.\,\;\)]", desc, re.IGNORECASE)
        if m:
            aka = m.group(1).strip()
            # Skip if captured text is too long (likely a full sentence fragment)
            if aka.lower() != term.lower() and len(aka) < 60:
                synonyms[aka.lower()] = term

        # 6. "It is also called XXX" pattern
        m = re.search(r"it is also called\s+(?:the\s+)?(.+?)[\.\,\)]", desc, re.IGNORECASE)
        if m:
            alias = m.group(1).strip()
            if alias.lower() != term.lower():
                synonyms[alias.lower()] = term

    # Clean up
    cleaned = {}
    for k, v in synonyms.items():
        # Skip self-referencing
        if k == v.lower():
            continue
        # Skip keys with unbalanced parens (broken regex captures)
        if k.count("(") != k.count(")"):
            continue
        # Skip very short keys (1 char) — too ambiguous
        if len(k) <= 1:
            continue
        cleaned[k] = v

    return dict(sorted(cleaned.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build glossary JSON files from a glossary CSV.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to glossary CSV")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Output directory for JSON files")
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Error: CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Load and build
    rows = load_csv(args.csv)
    glossary = build_glossary(rows)
    synonym_map = build_synonym_map(rows, glossary)

    # Write outputs
    glossary_path = args.out_dir / "glossary.json"
    synonym_path = args.out_dir / "synonym-map.json"

    with open(glossary_path, "w", encoding="utf-8") as f:
        json.dump(glossary, f, indent=2, ensure_ascii=False)

    with open(synonym_path, "w", encoding="utf-8") as f:
        json.dump(synonym_map, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"Glossary: {len(glossary)} terms → {glossary_path}")
    print(f"Synonym map: {len(synonym_map)} mappings → {synonym_path}")

    # Show synonym samples
    print("\nSynonym samples:")
    for k, v in list(synonym_map.items())[:10]:
        print(f"  {k!r} → {v!r}")


if __name__ == "__main__":
    main()
