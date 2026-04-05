#!/usr/bin/env python3
"""
Initialize a session at the start of a skill call.

Detects the current Claude Code session ID, generates the full session name,
and creates the history directory. Fails immediately if detection fails.

Usage:
    uv run skills/_shared/scripts/init_session.py --domain customer-service
    uv run skills/_shared/scripts/init_session.py --domain marketing

Output (JSON):
    {"session_id": "cs_20260126_001_26feb511-...", "session_dir": "..."}
"""

import json
import sys

from autoservice.session import init_session


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Initialize session directory')
    parser.add_argument('--domain', required=True,
                        choices=['customer-service', 'marketing'],
                        help='Skill domain')
    args = parser.parse_args()

    session_id, session_dir = init_session(args.domain)
    print(json.dumps({
        'session_id': session_id,
        'session_dir': str(session_dir),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
