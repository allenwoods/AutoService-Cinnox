#!/usr/bin/env python3
"""
Get a record from the marketing database.

Usage:
    uv run scripts/get_record.py --type customer --name '王建华'
    uv run scripts/get_record.py --type product --id 'abc123'
"""

import argparse
import json
import sys

from autoservice.database import get_record
from autoservice.config import get_domain_config

DOMAIN = 'marketing'


def main():
    parser = argparse.ArgumentParser(description='Get a record from the marketing database')
    parser.add_argument('--type', required=True, choices=['product', 'customer', 'operator'],
                        help='Type of record to get')
    parser.add_argument('--name', help='Name of the record')
    parser.add_argument('--id', help='ID of the record')

    args = parser.parse_args()

    if not args.name and not args.id:
        print("Error: Must provide either --name or --id", file=sys.stderr)
        sys.exit(1)

    search_term = args.name or args.id
    config = get_domain_config(DOMAIN)

    data, item_dir = get_record(DOMAIN, args.type, search_term, config)

    if data is None:
        print(f"Error: Record not found: {search_term}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\nLocation: {item_dir}")


if __name__ == '__main__':
    main()
