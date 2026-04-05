#!/usr/bin/env python3
"""
Query the mock/real API from the command line.

Usage:
    uv run skills/_shared/scripts/query_api.py \
        --domain customer-service \
        --endpoint "/api/v1/customers/13800138000"

    uv run skills/_shared/scripts/query_api.py \
        --domain marketing \
        --endpoint "/api/v1/products/prod001/pricing" \
        --params '{"customer_tier": "enterprise"}'
"""

import argparse
import json
import sys

from autoservice.api_client import APIClient, format_api_response


def main():
    parser = argparse.ArgumentParser(description="Query API endpoint")
    parser.add_argument("--domain", required=True, choices=["marketing", "customer-service"])
    parser.add_argument("--endpoint", required=True, help="API endpoint path (e.g., /api/v1/customers/123)")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT"])
    parser.add_argument("--params", default=None, help="JSON params for query string (GET) or body (POST/PUT)")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON instead of formatted display")
    args = parser.parse_args()

    client = APIClient(domain=args.domain)
    params = json.loads(args.params) if args.params else None

    try:
        if args.method == "GET":
            response = client.get(args.endpoint, params)
        elif args.method == "POST":
            response = client.post(args.endpoint, params or {})
        elif args.method == "PUT":
            response = client.put(args.endpoint, params or {})
        else:
            print(json.dumps({"error": f"Unsupported method: {args.method}"}))
            sys.exit(1)

        if args.raw:
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            print(format_api_response(response, f"{args.method} {args.endpoint}"))

    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "mode": "mock",
        }
        if args.raw:
            print(json.dumps(error_response, ensure_ascii=False))
        else:
            print(format_api_response(error_response, f"{args.method} {args.endpoint}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
