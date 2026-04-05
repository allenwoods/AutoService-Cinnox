#!/usr/bin/env python3
"""
List records in customer service database.

Usage:
    uv run list_records.py [--type <product|customer|operator|all>] [--verbose]
"""

import argparse
import json
import sys

from autoservice.database import list_records, print_results
from autoservice.config import get_domain_config

DOMAIN = 'customer-service'


def main():
    parser = argparse.ArgumentParser(description='List customer service records')
    parser.add_argument('--type', choices=['product', 'customer', 'operator', 'all'],
                        default='all', help='Type of records to list')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed information')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    try:
        config = get_domain_config(DOMAIN)
        results = list_records(DOMAIN, args.type, args.verbose, config)

        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_results(results, config, args.verbose)

            # Summary
            total = sum(len(items) for items in results.values())
            print(f"\n总计: {total} 条记录")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
