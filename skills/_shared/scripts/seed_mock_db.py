#!/usr/bin/env python3
"""
Seed SQLite mock database from JSON mock data.

Reads JSON files from the domain database directory and populates
the SQLite mock database with relational data for API serving.

Usage:
    uv run skills/_shared/scripts/seed_mock_db.py --domain marketing
    uv run skills/_shared/scripts/seed_mock_db.py --domain customer-service
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from autoservice.mock_db import MockDB


def gen_id(prefix: str, name: str) -> str:
    """Generate a deterministic ID from prefix + name."""
    h = hashlib.md5(name.encode()).hexdigest()[:8]
    return f"{prefix}_{h}"


def seed_from_json_files(db: MockDB, database_path: Path, domain: str):
    """Seed the mock DB from JSON files in the database directory."""
    products_dir = database_path / "products"
    customers_dir = database_path / "customers"
    operators_dir = database_path / "operators"

    products = []
    customers = []

    # --- Seed products ---
    if products_dir.exists():
        for product_dir in products_dir.iterdir():
            if not product_dir.is_dir():
                continue
            info_file = product_dir / "info.json"
            if not info_file.exists():
                continue

            product = json.loads(info_file.read_text(encoding="utf-8"))
            products.append(product)
            product_id = product.get("_id", "")

            # Upsert product
            db.upsert_product(product)

            # Seed product pricing
            pricing_data = {
                "product_id": product_id,
                "base_price": _extract_price(product),
                "volume_discount": product.get("volume_discount", ""),
                "special_offers": product.get("special_offers", []),
                "trial_options": product.get("trial_options", {}),
            }
            # For marketing products
            if "price_range" in product:
                pricing_data["volume_discount"] = product.get("price_range", "")
            db.set_product_pricing(pricing_data)

            # Seed product features from features list
            features = product.get("features", [])
            for feat in features:
                feat_name = feat if isinstance(feat, str) else str(feat)
                db.add_product_feature({
                    "product_id": product_id,
                    "feature_name": feat_name,
                    "is_available": True,
                    "release_date": "2025-01-01",
                    "tier_required": "standard",
                })

            # Seed permission rules
            permissions = product.get("operator_permissions", {})
            if permissions:
                db.set_permission_rules(product_id, domain, permissions)

            # Seed services from product
            service_id = gen_id("svc", product.get("name", ""))
            db.add_service({
                "id": service_id,
                "name": product.get("name", ""),
                "price": _extract_price(product),
                "period": "月",
                "category": product.get("category", domain),
                "description": product.get("description", ""),
            })

    # --- Seed customers ---
    if customers_dir.exists():
        for customer_dir in customers_dir.iterdir():
            if not customer_dir.is_dir():
                continue
            info_file = customer_dir / "info.json"
            if not info_file.exists():
                continue

            customer = json.loads(info_file.read_text(encoding="utf-8"))
            customers.append(customer)
            customer_id = customer.get("_id", "")

            # Upsert customer
            db.upsert_customer(customer)

            # Generate mock subscriptions for this customer
            if products:
                _seed_customer_subscriptions(db, customer_id, products, domain)

            # Generate mock billing
            _seed_customer_billing(db, customer_id, products)

            # Generate mock orders (mainly for customer-service)
            if domain == "customer-service" or domain == "customer_service":
                _seed_customer_orders(db, customer_id, products)

    # Summary
    result = {
        "status": "success",
        "domain": domain,
        "seeded": {
            "products": len(products),
            "customers": len(customers),
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _extract_price(product: dict) -> float:
    """Extract numeric price from product data."""
    price = product.get("price", 0)
    if isinstance(price, (int, float)):
        return float(price)
    if isinstance(price, str):
        import re
        numbers = re.findall(r'[\d.]+', price)
        if numbers:
            return float(numbers[0])
    return 0.0


def _seed_customer_subscriptions(db: MockDB, customer_id: str, products: list, domain: str):
    """Create mock subscriptions linking customers to products."""
    today = datetime.now()
    for i, product in enumerate(products):
        product_name = product.get("name", f"产品{i}")
        product_id = product.get("_id", "")
        fee = _extract_price(product)

        sub_id = gen_id("sub", f"{customer_id}_{product_name}")
        start = today - timedelta(days=30 * (i + 1))
        end = start + timedelta(days=365)

        db.add_subscription({
            "id": sub_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "service_name": product_name,
            "fee": fee if fee < 1000 else fee / 12,  # Normalize to monthly
            "status": "active",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "auto_renew": True,
        })


def _seed_customer_billing(db: MockDB, customer_id: str, products: list):
    """Create mock billing transactions."""
    today = datetime.now()
    for i, product in enumerate(products):
        product_name = product.get("name", f"产品{i}")
        fee = _extract_price(product)
        if fee > 1000:
            fee = fee / 12  # Normalize to monthly

        # Create 3 months of billing
        for month in range(3):
            txn_date = today - timedelta(days=30 * month)
            txn_id = gen_id("txn", f"{customer_id}_{product_name}_{month}")
            db.add_billing_transaction({
                "id": txn_id,
                "customer_id": customer_id,
                "type": "subscription",
                "description": f"{product_name}月费",
                "amount": fee,
                "date": txn_date.strftime("%Y-%m-%d"),
                "status": "completed",
                "related_subscription_id": gen_id("sub", f"{customer_id}_{product_name}"),
            })


def _seed_customer_orders(db: MockDB, customer_id: str, products: list):
    """Create mock orders for customer-service scenarios."""
    today = datetime.now()
    for i, product in enumerate(products):
        product_name = product.get("name", f"产品{i}")
        price = _extract_price(product)
        order_id = gen_id("ord", f"{customer_id}_{product_name}")
        order_date = today - timedelta(days=10 * (i + 1))

        db.add_order({
            "id": order_id,
            "customer_id": customer_id,
            "product": product_name,
            "price": price,
            "status": "delivered",
            "delivery_carrier": "顺丰快递",
            "delivery_tracking": f"SF{abs(hash(order_id)) % 10000000000:010d}",
            "delivery_eta": (order_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "payment_status": "paid",
            "date": order_date.strftime("%Y-%m-%d"),
        })


def main():
    parser = argparse.ArgumentParser(description="Seed mock database from JSON files")
    parser.add_argument("--domain", required=True, choices=["marketing", "customer-service"])
    args = parser.parse_args()

    domain_dir = args.domain.replace('-', '_')
    database_path = Path(f".autoservice/database/{domain_dir}")
    db_path = database_path / "mock.db"

    if not database_path.exists():
        print(json.dumps({"error": f"Database directory not found: {database_path}"}))
        sys.exit(1)

    db = MockDB(str(db_path))
    seed_from_json_files(db, database_path, args.domain)


if __name__ == "__main__":
    main()
