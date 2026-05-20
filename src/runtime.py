# src/runtime.py

from typing import Any, Dict

from data_loader import load_user, load_vendor
from decision import make_decision
from db import save_transaction, save_decision, create_approval


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

    action = decision_result["action"]
    transaction_id = transaction.get("transaction_id")

    save_transaction(
        user_id=user_id,
        vendor_id=vendor_id,
        transaction=transaction,
        status=action,
    )

    save_decision(
        transaction_id=transaction_id,
        decision_result=decision_result,
    )

    if action == "REQUIRE_APPROVAL":
        create_approval(transaction_id)

    return {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "vendor_name": vendor.get("name"),
        "transaction": transaction,
        **decision_result,
    }