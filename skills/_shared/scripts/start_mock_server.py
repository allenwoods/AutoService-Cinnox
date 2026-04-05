#!/usr/bin/env python3
"""
Start the mock API server for a domain.

Usage:
    uv run skills/_shared/scripts/start_mock_server.py --domain marketing
    uv run skills/_shared/scripts/start_mock_server.py --domain customer-service --port 8100
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


def find_free_port() -> int:
    """Find a free port to bind to."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description="Start mock API server")
    parser.add_argument("--domain", required=True, choices=["marketing", "customer-service"])
    parser.add_argument("--port", type=int, default=0, help="Port (0 = auto)")
    args = parser.parse_args()

    domain_dir = args.domain.replace('-', '_')
    db_path = Path(f".autoservice/database/{domain_dir}/mock.db")
    info_path = Path(f".autoservice/database/{domain_dir}/.mock_server_info")

    if not db_path.exists():
        print(json.dumps({"error": f"Mock database not found: {db_path}. Run 'create --mock' first."}))
        sys.exit(1)

    # Check if server already running
    if info_path.exists():
        try:
            info = json.loads(info_path.read_text())
            pid = info.get("pid")
            if pid:
                os.kill(pid, 0)  # Check if process exists
                print(json.dumps({"status": "already_running", "port": info["port"], "pid": pid, "url": info["url"]}))
                return
        except (ProcessLookupError, OSError):
            # Process not running, clean up stale info
            info_path.unlink(missing_ok=True)

    port = args.port or find_free_port()

    # Path to the shared directory
    shared_dir = Path(__file__).parent.parent

    # Start uvicorn as subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = str(shared_dir) + os.pathsep + env.get("PYTHONPATH", "")
    env["MOCK_DB_PATH"] = str(db_path.absolute())
    env["MOCK_DOMAIN"] = args.domain

    # Create a small runner script inline
    runner_code = f"""
import sys
import os
os.chdir("{Path.cwd()}")
from autoservice.mock_api_server import create_app
app = create_app("{db_path.absolute()}", "{args.domain}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port={port}, log_level="warning")
"""

    runner_path = Path(f".autoservice/database/{domain_dir}/.mock_runner.py")
    runner_path.parent.mkdir(parents=True, exist_ok=True)
    runner_path.write_text(runner_code)

    proc = subprocess.Popen(
        [sys.executable, str(runner_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Wait for server to be ready
    url = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.2)
    else:
        print(json.dumps({"error": "Server failed to start within timeout"}))
        proc.kill()
        sys.exit(1)

    # Save server info
    server_info = {
        "port": port,
        "pid": proc.pid,
        "url": url,
        "domain": args.domain,
        "db_path": str(db_path),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    info_path.write_text(json.dumps(server_info, indent=2))

    print(json.dumps(server_info))


if __name__ == "__main__":
    main()
