# src/decision.py

from typing import Any, Dict

from trust_score import evaluate_trust_score, is_blacklisted


ALLOW = "ALLOW"
ANNOUNCE = "ANNOUNCE"
REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DENY = "DENY"

ALLOW_SCORE_THRESHOLD = 90.0
ANNOUNCE_SCORE_THRESHOLD = 70.0
REQUIRE_APPROVAL_SCORE_THRESHOLD = 50.0

DENY_RISK_FLAGS = {
    "BLACKLISTED_VENDOR",
    "HAS_PHISHING_REPORT",
    "HAS_PROMPT_INJECTION_REPORT",
}

REQUIRE_APPROVAL_RISK_FLAGS = {
    "UNKNOWN_RECEIVER_ADDRESS",
    "UNKNOWN_SERVICE_ID",
    "AMOUNT_EXCEEDS_MAX_REASONABLE_PRICE",
    "DAILY_BUDGET_EXCEEDED",
    "PER_VENDOR_DAILY_BUDGET_EXCEEDED",
    "ADDRESS_CHANGED_RECENTLY",
}


def is_transaction_valid(transaction: Dict[str, Any]) -> bool:
    return transaction.get("amount_usd", 0) > 0


def get_action_by_score(score: float) -> str:
    if score >= ALLOW_SCORE_THRESHOLD:
        return ALLOW
    elif score >= ANNOUNCE_SCORE_THRESHOLD:
        return ANNOUNCE
    elif score >= REQUIRE_APPROVAL_SCORE_THRESHOLD:
        return REQUIRE_APPROVAL
    else:
        return DENY


def apply_risk_override(action: str, risk_flags: list[str]) -> str:
    risk_flag_set = set(risk_flags)

    if risk_flag_set & DENY_RISK_FLAGS:
        return DENY

    if risk_flag_set & REQUIRE_APPROVAL_RISK_FLAGS:
        if action in {ALLOW, ANNOUNCE}:
            return REQUIRE_APPROVAL

    return action


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
            "risk_flags": ["INVALID_TRANSACTION"],
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
    risk_flags = trust_result.get("risk_flags", [])

    action = get_action_by_score(score)
    action = apply_risk_override(action, risk_flags)

    return {
        **trust_result,
        "action": action,
    }