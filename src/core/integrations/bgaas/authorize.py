# HTTP POST /authorize 的業務入口（佔位）；之後接 core.runtime.process_transaction + 簽章。

from __future__ import annotations

from .types import AuthorizationResponse, PaymentIntentPayload


def authorize_payment_intent(
    intent: PaymentIntentPayload,
    *,
    user_id: str,
    vendor_id: str,
) -> AuthorizationResponse:
    """
    TODO: 呼叫 process_transaction、寫 db、產 EIP-712 / HMAC 簽章。
    """
    return {
        "decision": "TODO",
        "trust_score": 0.0,
        "signature": None,
        "raw": {
            "intent": dict(intent),
            "user_id": user_id,
            "vendor_id": vendor_id,
            "message": "PLACEHOLDER: authorize_payment_intent",
        },
    }
