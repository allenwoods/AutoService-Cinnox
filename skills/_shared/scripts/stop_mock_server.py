#!/usr/bin/env python3
"""
Stop the mock API server for a domain.

Usage:
    uv run skills/_shared/scripts/stop_mock_server.py --domain marketing
"""

import argparse
import json
import os
import signal
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Stop mock API server")
    parser.add_argument("--domain", required=True, choices=["marketing", "customer-service"])
    args = parser.parse_args()

    domain_dir = args.domain.replace('-', '_')
    info_path = Path(f".autoservice/database/{domain_dir}/.mock_server_info")

    if not info_path.exists():
        print(json.dumps({"status": "not_running", "message": "No server info found"}))
        return

    info = json.loads(info_path.read_text())
    pid = info.get("pid")

    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(json.dumps({"status": "stopped", "pid": pid, "port": info.get("port")}))
        except ProcessLookupError:
            print(json.dumps({"status": "already_stopped", "pid": pid}))
        except PermissionError:
            print(json.dumps({"error": f"Permission denied to stop process {pid}"}))
            sys.exit(1)

    # Clean up
    info_path.unlink(missing_ok=True)

    # Clean up runner script
    runner_path = Path(f".autoservice/database/{domain_dir}/.mock_runner.py")
    runner_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
