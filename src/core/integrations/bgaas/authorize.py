"""HTTP POST /authorize 業務入口：runtime 裁決 + EIP-712 簽章。"""

from __future__ import annotations

from ...infra.db import get_approval_by_transaction_id, get_decision_by_transaction_id
from ...runtime import process_transaction
from ...trust import ALLOW, ANNOUNCE, REQUIRE_APPROVAL
from .eip712 import sign_authorization
from .types import AuthorizationResponse, PaymentIntentPayload, intent_to_transaction


def _authorize_after_approval(transaction_id: str) -> AuthorizationResponse | None:
    approval = get_approval_by_transaction_id(transaction_id)
    if not approval or approval.get("status") != "APPROVED":
        return None
    stored = get_decision_by_transaction_id(transaction_id)
    if not stored:
        return None
    trust_score = float(stored["trust_score"])
    signature, signer_address, deadline = sign_authorization(
        transaction_id=transaction_id,
        decision=ALLOW,
        trust_score=trust_score,
    )
    return {
        "decision": ALLOW,
        "trust_score": trust_score,
        "signature": signature,
        "transaction_id": transaction_id,
        "deadline": deadline,
        "signer_address": signer_address,
        "risk_flags": list(stored.get("risk_flags") or []),
        "scores": {
            "identity": float(stored["identity_score"]),
            "reputation": float(stored["reputation_score"]),
            "behavior": float(stored["behavior_score"]),
            "user_policy": float(stored["user_policy_score"]),
        },
        "raw": {
            "mode": "after_approval",
            "prior_action": stored.get("action"),
        },
    }


def authorize_payment_intent(
    intent: PaymentIntentPayload,
    *,
    user_id: str,
    vendor_id: str,
    force_after_approval: bool = False,
) -> AuthorizationResponse:
    transaction = intent_to_transaction(intent)
    tx_id = transaction.get("transaction_id")

    if force_after_approval and tx_id:
        existing = _authorize_after_approval(str(tx_id))
        if existing:
            return existing

    result = process_transaction(
        user_id=user_id,
        vendor_id=vendor_id,
        transaction=transaction,
    )

    action = str(result.get("action", "DENY"))
    trust_score = float(result.get("trust_score", 0.0))
    tx = result.get("transaction") or {}
    transaction_id = str(tx.get("transaction_id", ""))

    sign_decision = action
    if (
        force_after_approval
        and action == REQUIRE_APPROVAL
        and transaction_id
    ):
        row = get_approval_by_transaction_id(transaction_id)
        if row and row.get("status") == "APPROVED":
            sign_decision = ALLOW

    signature, signer_address, deadline = sign_authorization(
        transaction_id=transaction_id,
        decision=sign_decision,
        trust_score=trust_score,
    )

    return {
        "decision": action,
        "trust_score": trust_score,
        "signature": signature,
        "transaction_id": transaction_id,
        "deadline": deadline,
        "signer_address": signer_address,
        "risk_flags": list(result.get("risk_flags") or []),
        "scores": dict(result.get("scores") or {}),
        "raw": {
            "intent": dict(intent),
            "user_id": user_id,
            "vendor_id": vendor_id,
            "sign_decision": sign_decision,
            "vendor_name": result.get("vendor_name"),
        },
    }
