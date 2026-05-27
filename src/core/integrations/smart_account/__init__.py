"""
Smart Account 硬攔截軌（Phase 7 占位）。

預期：validateUserOp / Plugin 在執行前呼叫 BGaaS /authorize 並驗證 EIP-712。
"""

from __future__ import annotations

from typing import Any


def validate_user_operation_before_execution(
    user_op: dict[str, Any],
    *,
    bgaas_base_url: str = "http://127.0.0.1:8000",
) -> dict[str, Any]:
    """占位：鏈上 module 應在此呼叫 BG 並檢查 signature。"""
    _ = (user_op, bgaas_base_url)
    return {
        "allowed": False,
        "reason": "NOT_IMPLEMENTED: Smart Account plugin track (Phase 7)",
        "next_step": "Wire MetaMask Delegation Toolkit or Safe Guard to POST /authorize + /verify",
    }
