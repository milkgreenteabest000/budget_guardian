from typing import Any, Dict

from .trust_score import evaluate_trust_score, is_blacklisted


ALLOW = "ALLOW"
ANNOUNCE = "ANNOUNCE"
REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DENY = "DENY"

ALLOW_SCORE_THRESHOLD = 90.0
ANNOUNCE_SCORE_THRESHOLD = 70.0
REQUIRE_APPROVAL_SCORE_THRESHOLD = 50.0


def is_transaction_valid(transaction: Dict[str, Any]) -> bool:
    return transaction.get("amount_usd", 0) > 0


def make_decision(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    if not is_transaction_valid(transaction):
        return {
            "trust_score": 0.0,
            "scores": {
                "identity": 0.0,
                "reputation": 0.0,
                "behavior": 0.0,
                "user_policy": 0.0,
            },
            "risk_flags": [],
            "action": DENY,
            "reason": "INVALID_TRANSACTION",
        }

    if is_blacklisted(user, vendor):
        return {
            "trust_score": 0.0,
            "scores": {
                "identity": 0.0,
                "reputation": 0.0,
                "behavior": 0.0,
                "user_policy": 0.0,
            },
            "risk_flags": ["BLACKLISTED_VENDOR"],
            "action": DENY,
            "reason": "BLACKLISTED_VENDOR",
        }

    trust_result = evaluate_trust_score(
        user=user,
        vendor=vendor,
        transaction=transaction,
    )

    score = trust_result["trust_score"]

    if score >= ALLOW_SCORE_THRESHOLD:
        action = ALLOW
    elif score >= ANNOUNCE_SCORE_THRESHOLD:
        action = ANNOUNCE
    elif score >= REQUIRE_APPROVAL_SCORE_THRESHOLD:
        action = REQUIRE_APPROVAL
    else:
        action = DENY

    return {
        **trust_result,
        "action": action,
    }
