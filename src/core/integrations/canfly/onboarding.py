from __future__ import annotations

from typing import Any

from .state_store import get_agent, load_state, save_state, _now


def prompt_md_edit_authorization(agent_id: str, user_id: str | None) -> dict[str, Any]:
    _ = user_id
    return {
        "agent_id": agent_id,
        "prompt": "Allow Budget Guardian to update memory.md with payment governance rules?",
        "status": "PENDING",
    }


def grant_md_consent(agent_id: str, user_id: str | None, *, allowed: bool = True) -> dict[str, Any]:
    _ = user_id
    state = load_state()
    agent = state.setdefault("agents", {}).setdefault(agent_id, {})
    agent["md_consent"] = {
        "allowed": allowed,
        "recorded_at": _now() if allowed else None,
    }
    save_state(state)
    return {
        "ok": True,
        "agent_id": agent_id,
        "md_consent": agent["md_consent"],
    }


def apply_memory_template(agent_id: str, user_id: str | None) -> dict[str, Any]:
    _ = user_id
    agent = get_agent(agent_id)
    if not agent.get("md_consent", {}).get("allowed"):
        return {"ok": False, "message": "md consent not granted"}
    return {
        "ok": True,
        "agent_id": agent_id,
        "message": "memory.md template would be applied (demo placeholder)",
    }
