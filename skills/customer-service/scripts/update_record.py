#!/usr/bin/env python3
"""
Update a record in the customer service database.

Usage:
    uv run scripts/update_record.py --type customer --name '张先生' --updates '{"phone": "13800138001"}'
    uv run scripts/update_record.py --type product --id 'abc123' --updates '{"sla": "24小时响应"}'
"""

import argparse
import json
import sys

from autoservice.database import update_record
from autoservice.config import get_domain_config

DOMAIN = 'customer_service'


def main():
    parser = argparse.ArgumentParser(description='Update a record in the customer service database')
    parser.add_argument('--type', required=True, choices=['product', 'customer', 'operator'],
                        help='Type of record to update')
    parser.add_argument('--name', help='Name of the record')
    parser.add_argument('--id', help='ID of the record')
    parser.add_argument('--updates', required=True, help='JSON object with fields to update')

    args = parser.parse_args()

    if not args.name and not args.id:
        print("Error: Must provide either --name or --id", file=sys.stderr)
        sys.exit(1)

    try:
        updates = json.loads(args.updates)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON updates - {e}", file=sys.stderr)
        sys.exit(1)

    search_term = args.name or args.id
    config = get_domain_config(DOMAIN)

    result = update_record(DOMAIN, args.type, search_term, updates, config)

    if result is None:
        print(f"Error: Record not found: {search_term}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated: {result}")


if __name__ == '__main__':
    main()
