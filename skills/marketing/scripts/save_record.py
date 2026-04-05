#!/usr/bin/env python3
"""
Save a record (product, customer, or operator) to the marketing database.

Usage:
    uv run scripts/save_record.py --type customer --data '<json>'
    uv run scripts/save_record.py --type product --data '<json>'
    uv run scripts/save_record.py --type operator --data '<json>'
"""

import argparse
import json
import sys

from autoservice.database import save_record
from autoservice.config import get_domain_config

DOMAIN = 'marketing'


def main():
    parser = argparse.ArgumentParser(description='Save a record to the marketing database')
    parser.add_argument('--type', required=True, choices=['product', 'customer', 'operator'],
                        help='Type of record to save')
    parser.add_argument('--data', required=True, help='JSON data for the record')

    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data - {e}", file=sys.stderr)
        sys.exit(1)

    if 'name' not in data:
        print("Error: Record must have a 'name' field", file=sys.stderr)
        sys.exit(1)

    config = get_domain_config(DOMAIN)
    save_record(DOMAIN, args.type, data, config)


if __name__ == '__main__':
    main()
