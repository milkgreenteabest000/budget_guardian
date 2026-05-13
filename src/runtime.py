# src/runtime.py

from typing import Any, Dict

from data_loader import load_user, load_vendor
from decision import make_decision


def process_transaction(
    user_id: str,
    vendor_id: str,
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    user = load_user(user_id)
    vendor = load_vendor(vendor_id)

    decision_result = make_decision(
        user=user,
        vendor=vendor,
        transaction=transaction,
    )

    return {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "vendor_name": vendor.get("name"),
        "transaction": transaction,
        **decision_result,
    }