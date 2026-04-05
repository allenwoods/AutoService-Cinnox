"""
Cinnox plugin — MCP tool implementations.

Provides customer lookup, billing, subscription, and permission
check tools backed by autoservice.mock_db.MockDB.
"""

from datetime import datetime
from typing import Optional

from autoservice.mock_db import MockDB
from autoservice.permission import check_permission


# The plugin loader injects the DB instance at load time.
# Tools receive it via the plugin's db attribute during dispatch.
# For standalone usage, callers must set _db before calling.
_db: Optional[MockDB] = None


def _get_db() -> MockDB:
    if _db is None:
        raise RuntimeError("MockDB not initialized — call set_db() first")
    return _db


def set_db(db: MockDB) -> None:
    """Set the shared MockDB instance for all tools."""
    global _db
    _db = db


def _envelope(data=None, error=None) -> dict:
    """Wrap response in standard API envelope."""
    return {
        "success": error is None,
        "data": data,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "mode": "mock",
    }


# --------------------------------------------------------------------------
# MCP Tools
# --------------------------------------------------------------------------

def customer_lookup(identifier: str) -> dict:
    """Look up a CINNOX customer by account ID, phone, or company name."""
    db = _get_db()
    customer = db.get_customer(identifier)
    if not customer:
        return _envelope(error=f"Customer not found: {identifier}")
    db.log_api_call(f"/api/cinnox/customers/{identifier}", "GET", response=customer)
    return _envelope(data=customer)


def billing_query(account_id: str, start_date: str = None, end_date: str = None) -> dict:
    """Get customer billing history and invoice status."""
    db = _get_db()
    customer = db.get_customer(account_id)
    if not customer:
        return _envelope(error=f"Customer not found: {account_id}")
    actual_id = customer["id"]
    result = db.get_billing(actual_id, start_date, end_date)
    db.log_api_call(f"/api/cinnox/customers/{account_id}/billing", "GET", response=result)
    return _envelope(data=result)


def subscription_query(account_id: str) -> dict:
    """Get active subscriptions and DID numbers."""
    db = _get_db()
    customer = db.get_customer(account_id)
    if not customer:
        return _envelope(error=f"Customer not found: {account_id}")
    actual_id = customer["id"]
    subs = db.get_subscriptions(actual_id)
    result = {"subscriptions": subs}
    db.log_api_call(f"/api/cinnox/customers/{account_id}/subscriptions", "GET", response=result)
    return _envelope(data=result)


def permission_check(action: str, product_id: str = None) -> dict:
    """Check if an action is permitted for the current operator."""
    db = _get_db()

    # Get product-specific permissions from DB if a product_id is given
    product_permissions = None
    if product_id:
        product_data = db.get_product_full_data(product_id)
        if product_data:
            product_permissions = product_data.get("operator_permissions")

    result = check_permission(
        action=action,
        product_permissions=product_permissions,
        domain="customer-service",
    )
    response = {
        "action": result.action,
        "level": result.level.value,
        "allowed": result.allowed,
        "reason": result.reason,
        "workflow": result.workflow,
        "display": result.to_display_block(),
    }
    db.log_api_call("/api/cinnox/permissions/check", "POST",
                    params={"action": action, "product_id": product_id},
                    response=response)
    return _envelope(data=response)
