# Agent 對外 HTTP／付費意圖的攔截掛勾（佔位）。

from __future__ import annotations

from typing import Any


def should_intercept_request(
    agent_id: str,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    TODO: 依 Canfly runtime 能力，判斷是否需先走 BG（例如 402、付費網域）。
    """
    return {
        "intercept": False,
        "agent_id": agent_id,
        "method": method,
        "url": url,
        "message": "PLACEHOLDER: interception policy",
    }


def before_outbound_request(
    agent_id: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    TODO: 在實際送出前呼叫 bgaas.authorize（或快取），必要時改寫 headers。
    """
    return {
        "allow": True,
        "agent_id": agent_id,
        "context_keys": list(context.keys()),
        "message": "PLACEHOLDER: pre-flight BG check",
    }
