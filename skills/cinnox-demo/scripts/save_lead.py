#!/usr/bin/env python3
"""
Save a collected lead from the CINNOX demo session.

Usage:
    uv run .claude/skills/cinnox-demo/scripts/save_lead.py \
        --type new_customer \
        --data '{"name": "Alice", "company": "Acme", "email": "alice@acme.com", "phone": "+1234567890"}'
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path.cwd()
LEADS_DIR = PROJECT_ROOT / ".autoservice" / "database" / "knowledge_base" / "leads"


def main():
    parser = argparse.ArgumentParser(description="Save a CINNOX demo lead")
    parser.add_argument(
        "--type",
        required=True,
        choices=["new_customer", "existing_customer", "partner"],
        help="Customer type",
    )
    parser.add_argument("--data", required=True, help="JSON data string")
    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}")
        sys.exit(1)

    LEADS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    record = {
        "type": args.type,
        "data": data,
        "created_at": now.isoformat(),
    }

    filename = f"{args.type}_{now.strftime('%Y%m%d_%H%M%S')}.json"
    lead_file = LEADS_DIR / filename
    lead_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[Lead Saved] {args.type}: {lead_file.name}")
    print(json.dumps({"status": "ok", "file": str(lead_file)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
