#!/usr/bin/env python3
"""
Save a completed sales demo session.

Usage:
    uv run skills/sales-demo/scripts/save_session.py \
        --customer-type "new_customer" \
        --resolution "resolved" \
        --conversation '[{"role":"bot","content":"Hi"},{"role":"user","content":"Hi"}]'
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path.cwd()
SESSIONS_DIR = PROJECT_ROOT / ".autoservice" / "database" / "knowledge_base" / "sessions"


def main():
    parser = argparse.ArgumentParser(description="Save a sales demo session")
    parser.add_argument(
        "--customer-type",
        default="unknown",
        choices=["new_customer", "existing_customer", "partner", "unknown"],
    )
    parser.add_argument(
        "--resolution",
        default="unknown",
        choices=["resolved", "transferred", "abandoned", "unknown"],
    )
    parser.add_argument("--conversation", default="[]", help="JSON array of conversation turns")
    parser.add_argument(
        "--session-id",
        default="",
        help="Existing web_session_id to update instead of creating a new file",
    )
    args = parser.parse_args()

    try:
        conversation = json.loads(args.conversation)
    except json.JSONDecodeError:
        conversation = []

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Try to update an existing session file ────────────────────────────
    session_id = args.session_id.strip()
    if session_id and re.match(r'^session_\d{8}_\d{6}$', session_id):
        existing = SESSIONS_DIR / f"{session_id}.json"
        if existing.exists():
            try:
                record = json.loads(existing.read_text(encoding="utf-8"))
                record["customer_type"] = args.customer_type
                record["resolution"] = args.resolution
                # Only replace conversation if the bot actually built one
                if conversation:
                    record["conversation"] = conversation
                    record["turn_count"] = len([t for t in conversation if t.get("role") == "user"])
                existing.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[Session Updated] {existing.name}")
                print(f"  Customer type : {args.customer_type}")
                print(f"  Resolution    : {args.resolution}")
                return
            except Exception as e:
                print(f"[warn] Could not update existing session: {e}", file=sys.stderr)

    # ── Fallback: create a new file (no valid session-id provided) ────────
    now = datetime.now()
    record = {
        "customer_type": args.customer_type,
        "resolution": args.resolution,
        "turn_count": len([t for t in conversation if t.get("role") == "user"]),
        "conversation": conversation,
        "created_at": now.isoformat(),
    }

    filename = f"session_{now.strftime('%Y%m%d_%H%M%S')}.json"
    session_file = SESSIONS_DIR / filename
    session_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[Session Saved] {filename}")
    print(f"  Customer type : {args.customer_type}")
    print(f"  Resolution    : {args.resolution}")
    print(f"  Turns         : {len(conversation)}")


if __name__ == "__main__":
    main()
