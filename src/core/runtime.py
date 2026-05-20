"""整體流程：載入 user/vendor → 裁決 → 寫 DB → 通知／狀態占位。"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from infra import notifications
from infra.data_loader import load_user, load_vendor
from infra.db import create_approval, save_decision, save_transaction
from trust import REQUIRE_APPROVAL, make_decision


def process_transaction(
    user_id: str,
    vendor_id: str,
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    user = load_user(user_id)
    vendor = load_vendor(vendor_id)

    tx = dict(transaction)

    if tx.get("transaction_id") in (None, ""):
        tx["transaction_id"] = f"tx_{uuid.uuid4().hex}"

    decision_result = make_decision(
        user=user,
        vendor=vendor,
        transaction=tx,
    )

    action = decision_result["action"]
    transaction_id = tx["transaction_id"]

    save_transaction(
        user_id=user_id,
        vendor_id=vendor_id,
        transaction=tx,
        status=action,
    )

    save_decision(
        transaction_id=transaction_id,
        decision_result=decision_result,
    )

    if action == REQUIRE_APPROVAL and transaction_id:
        create_approval(transaction_id)

    side_effect_result = notifications.apply_decision_side_effects(
        user_id=user_id,
        vendor_id=vendor_id,
        user=user,
        vendor=vendor,
        transaction=tx,
        decision_result=decision_result,
    )

    return {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "vendor_name": vendor.get("name"),
        "transaction": tx,
        **decision_result,
        "side_effect": side_effect_result,
    }