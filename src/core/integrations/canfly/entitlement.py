# 偵測「是否已購買本服務」與權益快取（佔位）。

from __future__ import annotations

from typing import Any

from core.infra.paths import DATA_DIR

from .models import EntitlementState

_PLACEHOLDER_STATE = DATA_DIR / "canfly_placeholder_state.json"


def load_entitlement(agent_id: str, user_id: str | None) -> EntitlementState:
    """
    TODO: 改為讀 Canfly billing / 自家後端；目前回傳固定佔位。
    預設資料檔：data/canfly_placeholder_state.json（尚未解析，仅占位路徑概念）。
    """
    _ = (agent_id, user_id, _PLACEHOLDER_STATE)
    return {
        "active": False,
        "product_sku": None,
        "expires_at": None,
    }


def record_purchase(agent_id: str, user_id: str | None, sku: str) -> dict[str, Any]:
    """TODO: 購買完成 callback 寫入權益。"""
    return {
        "ok": False,
        "agent_id": agent_id,
        "user_id": user_id,
        "sku": sku,
        "message": "PLACEHOLDER: persist entitlement",
    }
