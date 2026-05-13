# src/trust_score.py

from typing import Any, Dict


MIN_SCORE = 0.0
MAX_SCORE = 100.0

IDENTITY_WEIGHT = 0.30
REPUTATION_WEIGHT = 0.25
BEHAVIOR_WEIGHT = 0.30
USER_POLICY_WEIGHT = 0.15


def clamp(
    value: float,
    min_value: float = MIN_SCORE,
    max_value: float = MAX_SCORE,
) -> float:
    return max(min_value, min(max_value, value))


def is_blacklisted(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
) -> bool:
    vendor_id = vendor.get("vendor_id")

    return (
        vendor.get("blacklisted", False)
        or vendor_id in user.get("blocked_vendors", [])
    )


def calculate_identity(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
) -> float:
    if is_blacklisted(user, vendor):
        return 0.0

    score = 50.0
    vendor_id = vendor.get("vendor_id")

    if vendor.get("verified", False):
        score += 20

    if vendor.get("whitelisted", False):
        score += 10

    if vendor_id in user.get("trusted_vendors", []):
        score += 20

    if vendor.get("address_changed_recently", False):
        score -= 30

    return clamp(score)


def calculate_reputation(vendor: Dict[str, Any]) -> float:
    success_count = vendor.get("success_count", 0)
    fail_count = vendor.get("fail_count", 0)
    dispute_count = vendor.get("dispute_count", 0)

    total_count = success_count + fail_count + dispute_count

    score = 100 * (success_count + 3) / (total_count + 6)
    score -= fail_count * 1.5
    score -= dispute_count * 5

    return clamp(score)


def calculate_behavior(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
) -> float:
    score = 100.0

    if vendor.get("has_phishing_report", False):
        return 0.0

    if vendor.get("has_prompt_injection_report", False):
        return 0.0

    receiver_address = transaction.get("receiver_address", "").lower()
    valid_addresses = [
        address.lower()
        for address in vendor.get("receiver_addresses", [])
    ]

    if receiver_address not in valid_addresses:
        score -= 50

    service_id = transaction.get("service_id")
    valid_service_ids = vendor.get("service_ids", [])

    if service_id not in valid_service_ids:
        score -= 30

    amount_usd = transaction.get("amount_usd", 0)
    max_reasonable_price = vendor.get("max_reasonable_price_usd", 0)

    if max_reasonable_price > 0 and amount_usd > max_reasonable_price:
        score -= 30

    return clamp(score)


def calculate_user_policy(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
) -> float:
    if is_blacklisted(user, vendor):
        return 0.0

    vendor_id = vendor.get("vendor_id")
    amount_usd = transaction.get("amount_usd", 0)

    budget_policy = user.get("budget_policy", {})
    spending_state = user.get("spending_state", {})

    daily_budget = budget_policy.get("daily_total_budget_usd", 0)
    spent_today = spending_state.get("spent_today_usd", 0)

    if spent_today + amount_usd > daily_budget:
        return 0.0

    per_vendor_budget = budget_policy.get("per_vendor_daily_budget_usd", 0)
    per_vendor_spending = spending_state.get("per_vendor_spending_today", {})
    spent_to_vendor = per_vendor_spending.get(vendor_id, 0)

    if spent_to_vendor + amount_usd > per_vendor_budget:
        return 30.0

    if vendor_id in user.get("trusted_vendors", []):
        return 100.0

    return 70.0


def evaluate_trust_score(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    identity = calculate_identity(user, vendor)
    reputation = calculate_reputation(vendor)
    behavior = calculate_behavior(user, vendor, transaction)
    user_policy = calculate_user_policy(user, vendor, transaction)

    trust_score = (
        IDENTITY_WEIGHT * identity
        + REPUTATION_WEIGHT * reputation
        + BEHAVIOR_WEIGHT * behavior
        + USER_POLICY_WEIGHT * user_policy
    )

    trust_score = clamp(trust_score)

    return {
        "trust_score": round(trust_score, 2),
        "scores": {
            "identity": round(identity, 2),
            "reputation": round(reputation, 2),
            "behavior": round(behavior, 2),
            "user_policy": round(user_policy, 2),
        },
    }