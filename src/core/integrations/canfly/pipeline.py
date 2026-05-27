from __future__ import annotations

from . import entitlement, interception, onboarding
from .models import AgentGateResult, MdConsentState
from .state_store import get_agent


def run_canfly_agent_gate(
    agent_id: str,
    user_id: str | None = None,
    *,
    md_consent_granted: bool | None = None,
) -> AgentGateResult:
    ent = entitlement.load_entitlement(agent_id, user_id)
    notes: list[str] = []

    if not ent.get("active"):
        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "md_consent": {"allowed": False, "recorded_at": None},
            "entitlement": ent,
            "interception_enabled": False,
            "bgaas_hooks_enabled": False,
            "notes": notes + ["no entitlement: purchase required"],
        }

    rec = get_agent(agent_id)
    md: MdConsentState = {
        "allowed": bool(rec.get("md_consent", {}).get("allowed")),
        "recorded_at": rec.get("md_consent", {}).get("recorded_at"),
    }

    if md_consent_granted is True:
        onboarding.grant_md_consent(agent_id, user_id, allowed=True)
        rec = get_agent(agent_id)
        md = {
            "allowed": bool(rec.get("md_consent", {}).get("allowed")),
            "recorded_at": rec.get("md_consent", {}).get("recorded_at"),
        }
    elif md_consent_granted is False:
        onboarding.grant_md_consent(agent_id, user_id, allowed=False)
        md = {"allowed": False, "recorded_at": None}

    if not md.get("allowed"):
        notes.append("onboarding: md consent required")
        onboarding.prompt_md_edit_authorization(agent_id, user_id)
        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "md_consent": md,
            "entitlement": ent,
            "interception_enabled": False,
            "bgaas_hooks_enabled": False,
            "notes": notes,
        }

    _ = interception.should_intercept_request(agent_id, "GET", "https://api.example/paid")
    notes.append("interception and BG hooks enabled")
    return {
        "agent_id": agent_id,
        "user_id": user_id,
        "md_consent": md,
        "entitlement": ent,
        "interception_enabled": True,
        "bgaas_hooks_enabled": True,
        "notes": notes,
    }
