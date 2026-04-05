#!/usr/bin/env python3
"""
Delete a record from the customer service database.

Usage:
    uv run scripts/delete_record.py --type customer --name '张先生'
    uv run scripts/delete_record.py --type product --id 'abc123'
"""

import argparse
import sys

from autoservice.database import delete_record
from autoservice.config import get_domain_config

DOMAIN = 'customer_service'


def main():
    parser = argparse.ArgumentParser(description='Delete a record from the customer service database')
    parser.add_argument('--type', required=True, choices=['product', 'customer', 'operator'],
                        help='Type of record to delete')
    parser.add_argument('--name', help='Name of the record')
    parser.add_argument('--id', help='ID of the record')
    parser.add_argument('--force', action='store_true', help='Skip confirmation')

    args = parser.parse_args()

    if not args.name and not args.id:
        print("Error: Must provide either --name or --id", file=sys.stderr)
        sys.exit(1)

    search_term = args.name or args.id
    config = get_domain_config(DOMAIN)

    if not args.force:
        confirm = input(f"Delete {args.type} '{search_term}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled")
            sys.exit(0)

    result = delete_record(DOMAIN, args.type, search_term, config)

    if not result:
        print(f"Error: Record not found: {search_term}", file=sys.stderr)
        sys.exit(1)

    print(f"Deleted: {search_term}")


if __name__ == '__main__':
    main()
