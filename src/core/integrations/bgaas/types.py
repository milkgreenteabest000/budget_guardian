# 之後對齊 APAP：PaymentIntent、AuthorizationResponse（佔位）。

from __future__ import annotations

from typing import Any, TypedDict


class PaymentIntentPayload(TypedDict, total=False):
    intent_id: str
    user_id: str
    vendor_id: str
    service_id: str
    amount_usd: float
    receiver_address: str
    payment_reason: str


class AuthorizationResponse(TypedDict, total=False):
    decision: str
    trust_score: float
    signature: str | None
    raw: dict[str, Any]
