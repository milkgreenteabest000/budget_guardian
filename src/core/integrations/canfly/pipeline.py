# Canfly 端「首次授權 md → 權益 → 是否啟用攔截／BG」流程骨架（佔位）。

from __future__ import annotations

from . import entitlement, interception, onboarding
from .models import AgentGateResult, MdConsentState


def run_canfly_agent_gate(
    agent_id: str,
    user_id: str | None = None,
    *,
    md_consent_granted: bool | None = None,
) -> AgentGateResult:
    """
    佔位流程：
    1) 若無購買權益 → 不啟用攔截（引導購買／試用）。
    2) 若有權益但尚未記錄 md 授權 → 回 onboarding（請使用者同意改 memory.md）。
    3) 若權益 + 授權皆備 → interception / bgaas_hooks 標記為 True（實作 TODO）。
    """
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
            "notes": notes + ["PLACEHOLDER: no entitlement, skip hooks"],
        }

    md: MdConsentState = {"allowed": False, "recorded_at": None}
    if md_consent_granted is True:
        md = {"allowed": True, "recorded_at": None}
    elif md_consent_granted is False:
        md = {"allowed": False, "recorded_at": None}

    if not md.get("allowed"):
        notes.append("PLACEHOLDER: need memory.md edit consent (first purchase)")
        _ = onboarding.prompt_md_edit_authorization(agent_id, user_id)
        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "md_consent": md,
            "entitlement": ent,
            "interception_enabled": False,
            "bgaas_hooks_enabled": False,
            "notes": notes,
        }

    notes.append("PLACEHOLDER: hooks would register here")
    _ = interception.should_intercept_request(agent_id, "GET", "https://example.invalid")

    return {
        "agent_id": agent_id,
        "user_id": user_id,
        "md_consent": md,
        "entitlement": ent,
        "interception_enabled": True,
        "bgaas_hooks_enabled": True,
        "notes": notes + ["PLACEHOLDER: interception + BG API wiring"],
    }
