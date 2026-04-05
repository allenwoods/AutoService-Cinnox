#!/usr/bin/env python3
"""
Check operator permissions via the API.

Usage:
    uv run skills/_shared/scripts/check_permission.py \
        --domain customer-service \
        --action "退款50元" \
        --product-id "prod_001"
"""

import argparse
import json
import sys

from autoservice.api_client import APIClient, format_permission_response


def main():
    parser = argparse.ArgumentParser(description="Check operator permission")
    parser.add_argument("--domain", required=True, choices=["marketing", "customer-service"])
    parser.add_argument("--action", required=True, help="Action to check (e.g., '退款50元', '试用30天')")
    parser.add_argument("--product-id", required=True, help="Product ID for product-specific permissions")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON instead of formatted display")
    args = parser.parse_args()

    client = APIClient(domain=args.domain)

    try:
        response = client.check_permission(
            action=args.action,
            product_id=args.product_id,
            domain=args.domain,
        )

        if args.raw:
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            print(format_permission_response(response))

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
