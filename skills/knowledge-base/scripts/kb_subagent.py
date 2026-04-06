#!/usr/bin/env python3
"""
Knowledge Base Sub-Agent Script

A CLI wrapper around kb_search.search() that forces domain/region filtering
and returns structured JSON output for use by orchestrating agents.

Usage:
    uv run skills/knowledge-base/scripts/kb_subagent.py \
        --role region_specialist \
        --domain global_telecom \
        --region US \
        --query "DID pricing" \
        --top-k 5

    uv run skills/knowledge-base/scripts/kb_subagent.py \
        --role product_expert \
        --domain contact_center \
        --query "WhatsApp integration"
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add scripts directory to path so we can import kb_search
_scripts_dir = str(Path(__file__).parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from kb_search import search  # noqa: E402

# Map domain to source_filter IDs (must match sources_meta.json)
DOMAIN_SOURCE_MAP: dict[str, list[str]] = {
    "contact_center": ["f4", "f5", "f6", "w1", "w2"],
    "ai_sales_bot": ["f1", "f2", "f3"],
    "global_telecom": ["f7", "f8", "w4"],
}


def main():
    parser = argparse.ArgumentParser(description="KB sub-agent with domain/region filtering")
    parser.add_argument("--role", required=True, help="Agent role (e.g., region_specialist, product_expert)")
    parser.add_argument("--domain", help="Domain filter (ai_sales_bot, contact_center, global_telecom)")
    parser.add_argument("--region", help="Region filter (e.g., US, HK, SG)")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Max results (default: 5)")
    args = parser.parse_args()

    source_filter = DOMAIN_SOURCE_MAP.get(args.domain) if args.domain else None

    results = search(
        query=args.query,
        top_k=args.top_k,
        source_filter=source_filter,
    )

    # Build sources consulted list
    sources_consulted = []
    seen = set()
    for r in results:
        key = r["source_id"]
        if key not in seen:
            seen.add(key)
            sources_consulted.append(f"{r['source_name']} [{r['source_id']}]")

    output = {
        "role": args.role,
        "domain": args.domain or "",
        "region": args.region or "",
        "query": args.query,
        "results": results,
        "sources_consulted": sources_consulted,
        "result_count": len(results),
        "has_results": len(results) > 0,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
