#!/usr/bin/env python3
"""
Save a single customer service record (product, customer, or operator) from user input.

Usage:
    uv run save_record.py --type <product|customer|operator> --data '<json_data>'
"""

import argparse
import json
import sys

from autoservice.database import save_record
from autoservice.config import get_domain_config

DOMAIN = 'customer-service'


def main():
    parser = argparse.ArgumentParser(description='Save a customer service record')
    parser.add_argument('--type', choices=['product', 'customer', 'operator'], required=True)
    parser.add_argument('--data', required=True, help='JSON data string')

    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    try:
        config = get_domain_config(DOMAIN)
        save_record(DOMAIN, args.type, data, config)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
