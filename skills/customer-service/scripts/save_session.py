#!/usr/bin/env python3
"""
Save a customer service call session to history, with optional customer info update.

The session directory must already exist (created by init_session.py at call start).

Usage:
    uv run save_session.py --session-id <id> --product <name> --customer <name> --operator <name> --review '<json>' --conversation '<json>' [--update-customer '<json>']
"""

import argparse
import json
import sys

from autoservice.session import save_session
from autoservice.config import get_domain_config
from autoservice.customer_manager import CustomerManager

DOMAIN = 'customer-service'


def main():
    parser = argparse.ArgumentParser(description='Save customer service session')
    parser.add_argument('--session-id', required=True,
                        help='Pre-generated session ID (from init_session.py)')
    parser.add_argument('--product', required=True)
    parser.add_argument('--customer', required=True)
    parser.add_argument('--operator', required=True)
    parser.add_argument('--review', required=True, help='JSON review/summary data')
    parser.add_argument('--conversation', required=False, default='[]',
                        help='JSON array of conversation messages')
    parser.add_argument('--update-customer', required=False, default=None,
                        help='JSON object with customer fields to update (for cold-start customers)')

    args = parser.parse_args()

    try:
        review = json.loads(args.review)
        conversation = json.loads(args.conversation) if args.conversation else []
        customer_updates = json.loads(args.update_customer) if args.update_customer else None

        config = get_domain_config(DOMAIN)

        # Save session using pre-generated session ID
        session_path = save_session(
            DOMAIN,
            args.session_id,
            args.product,
            args.customer,
            args.operator,
            conversation,
            review,
            config
        )

        # Update customer info if provided
        if customer_updates:
            customer_manager = CustomerManager(DOMAIN, config)

            # Try to find customer by name
            customer_data, customer_dir = customer_manager.lookup_by_name(args.customer)

            if customer_data and customer_dir:
                # Prepare session info for interaction history
                session_info = {
                    'session_id': args.session_id,
                    'type': 'customer_service_call',
                    'summary': review.get('issue_summary', ''),
                    'outcome': review.get('resolution_status', ''),
                }

                # Update customer
                updated = customer_manager.update_customer(
                    customer_dir,
                    customer_updates,
                    session_info
                )
                print(f"Customer updated: {customer_dir}")
            else:
                print(f"Warning: Could not find customer '{args.customer}' to update")

        print(f"Session saved successfully")

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
