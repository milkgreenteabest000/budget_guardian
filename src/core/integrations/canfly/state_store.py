"""讀寫 data/canfly_placeholder_state.json。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...infra.paths import DATA_DIR

STATE_PATH = DATA_DIR / "canfly_placeholder_state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> dict[str, Any]:
    return {"agents": {}}


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return _default_state()
    with STATE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "agents" not in data:
        data["agents"] = {}
    return data


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_agent(agent_id: str) -> dict[str, Any]:
    state = load_state()
    agents = state.setdefault("agents", {})
    if agent_id not in agents:
        agents[agent_id] = {
            "entitlement": {"active": False, "product_sku": None, "expires_at": None},
            "md_consent": {"allowed": False, "recorded_at": None},
        }
        save_state(state)
    return agents[agent_id]
