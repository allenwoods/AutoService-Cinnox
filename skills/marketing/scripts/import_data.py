#!/usr/bin/env python3
"""
Data importer for marketing skill.
Supports importing from DOCX, PDF, and XLSX files.

Usage:
    uv run import_data.py --type <product|customer|operator> --file <path> [--output <output_dir>]
"""

import argparse
import sys
from pathlib import Path

from autoservice.importer import import_file, import_to_domain
from autoservice.config import get_domain_config

DOMAIN = 'marketing'


def main():
    parser = argparse.ArgumentParser(description='Import marketing data from documents')
    parser.add_argument('--type', choices=['product', 'customer', 'operator'], required=True)
    parser.add_argument('--file', required=True, help='Path to DOCX, PDF, or XLSX file')
    parser.add_argument('--output', required=False, help='Output directory (optional, uses domain default)')

    args = parser.parse_args()

    try:
        if args.output:
            # Use explicit output directory
            paths = import_file(args.file, args.output, args.type)
        else:
            # Use domain default directory
            config = get_domain_config(DOMAIN)
            paths = import_to_domain(DOMAIN, args.file, args.type, config)

        print(f"\nSuccessfully imported {len(paths)} {args.type}(s)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
