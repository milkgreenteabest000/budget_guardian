"""依裁決結果寄通知／更新狀態（占位，之後接 email／webhook／更新 spending_state）。"""

from __future__ import annotations

from typing import Any, Dict


def apply_decision_side_effects(
    *,
    user_id: str,
    vendor_id: str,
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
    decision_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    TODO: 讀 user.notification_policy；對 ANNOUNCE / REQUIRE_APPROVAL / DENY 發通知；
    TODO: 必要時更新 spending_state、approval 狀態等。
    """
    action = decision_result.get("action")
    policy = user.get("notification_policy", {})
    _ = (vendor_id, vendor, transaction, policy)

    return {
        "user_id": user_id,
        "action": action,
        "dispatched": False,
        "note": "PLACEHOLDER: notifications / state updates",
    }
