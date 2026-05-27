# PaymentIntent、AuthorizationResponse 與 runtime transaction 映射。

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
    transaction_id: str


class AuthorizationResponse(TypedDict, total=False):
    decision: str
    trust_score: float
    signature: str | None
    transaction_id: str | None
    deadline: int | None
    signer_address: str | None
    risk_flags: list[str]
    scores: dict[str, float]
    raw: dict[str, Any]


def intent_to_transaction(intent: PaymentIntentPayload) -> dict[str, Any]:
    """將 API PaymentIntent 轉成 runtime 使用的 transaction dict。"""
    tx: dict[str, Any] = {}
    if intent.get("transaction_id"):
        tx["transaction_id"] = intent["transaction_id"]
    if intent.get("service_id") is not None:
        tx["service_id"] = intent["service_id"]
    if intent.get("amount_usd") is not None:
        tx["amount_usd"] = intent["amount_usd"]
    if intent.get("receiver_address") is not None:
        tx["receiver_address"] = intent["receiver_address"]
    if intent.get("payment_reason") is not None:
        tx["payment_reason"] = intent["payment_reason"]
    return tx
