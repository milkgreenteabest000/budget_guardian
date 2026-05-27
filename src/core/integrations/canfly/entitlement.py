from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import EntitlementState
from .state_store import get_agent, load_state, save_state


def load_entitlement(agent_id: str, user_id: str | None) -> EntitlementState:
    _ = user_id
    agent = get_agent(agent_id)
    ent = agent.get("entitlement") or {}
    return {
        "active": bool(ent.get("active")),
        "product_sku": ent.get("product_sku"),
        "expires_at": ent.get("expires_at"),
    }


def record_purchase(agent_id: str, user_id: str | None, sku: str) -> dict[str, Any]:
    _ = user_id
    state = load_state()
    agent = state.setdefault("agents", {}).setdefault(
        agent_id,
        {
            "entitlement": {"active": False, "product_sku": None, "expires_at": None},
            "md_consent": {"allowed": False, "recorded_at": None},
        },
    )
    agent["entitlement"] = {
        "active": True,
        "product_sku": sku,
        "expires_at": None,
    }
    save_state(state)
    return {
        "ok": True,
        "agent_id": agent_id,
        "sku": sku,
        "message": "Entitlement recorded",
    }
