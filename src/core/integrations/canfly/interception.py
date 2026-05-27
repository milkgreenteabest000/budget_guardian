from __future__ import annotations

from typing import Any

import httpx

from .config import BG_API_BASE_URL


def should_intercept_request(agent_id: str, method: str, url: str) -> dict[str, Any]:
    _ = agent_id
    paid_hint = "402" in url or "payment" in url.lower()
    return {
        "intercept": paid_hint or method.upper() in {"POST", "PUT"},
        "reason": "outbound payment or mutating request",
        "url": url,
    }


def preflight_authorize(
    *,
    user_id: str,
    vendor_id: str,
    intent: dict[str, Any],
    force_after_approval: bool = False,
) -> dict[str, Any]:
    """呼叫本機 BGaaS POST /authorize。"""
    payload = {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "intent": intent,
        "force_after_approval": force_after_approval,
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(f"{BG_API_BASE_URL}/authorize", json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        return {
            "decision": "DENY",
            "trust_score": 0.0,
            "signature": None,
            "error": str(exc),
        }
