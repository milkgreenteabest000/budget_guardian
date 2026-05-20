# 之後會對齊 Canfly / Agent 識別與狀態；目前僅型別佔位。

from __future__ import annotations

from typing import Literal, TypedDict


class MdConsentState(TypedDict, total=False):
    """使用者是否允許 Skill 修改 memory.md（佔位）。"""

    allowed: bool
    recorded_at: str | None


class EntitlementState(TypedDict, total=False):
    """是否已購買／訂閱本服務（佔位）。"""

    active: bool
    product_sku: str | None
    expires_at: str | None


class AgentGateResult(TypedDict, total=False):
    """pipeline 回傳給上層（Skill / runtime）的摘要（佔位）。"""

    agent_id: str
    user_id: str | None
    md_consent: MdConsentState
    entitlement: EntitlementState
    interception_enabled: bool
    bgaas_hooks_enabled: bool
    notes: list[str]


ConsentStatus = Literal["UNKNOWN", "PENDING", "GRANTED", "DENIED"]
EntitlementStatus = Literal["UNKNOWN", "NONE", "ACTIVE", "EXPIRED"]
