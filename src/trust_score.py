# trustmodel.py

from typing import Dict, Any, List

def clamp(value: float, min_value: float = 0, max_value: float = 100) -> float:
    return max(min_value, min(max_value, value))


def calculate_identity_score(vendor: Dict[str, Any], user: Dict[str, Any]) -> float:
    # const
    VERIFIED = 20
    WHITELISTED = 10
    TRUSTED = 20
    ADDRESS_CHANGED = -30

    # reject if blacklisted or blocked
    if vendor.get("blacklisted", False):
        return 0

    if vendor.get("vendor_id") in user.get("blocked_vendors", []):
        return 0

    # calculate identity score
    score = 50

    if vendor.get("verified", False):
        score += VERIFIED

    if vendor.get("whitelisted", False):
        score += WHITELISTED

    if vendor.get("vendor_id") in user.get("trusted_vendors", []):
        score += TRUSTED

    if vendor.get("address_changed_recently", False):
        score -= ADDRESS_CHANGED

    return clamp(score)


def calculate_reputation_score(vendor: Dict[str, Any]) -> float:
    # use Bayesian average to calculate reputation score
    success_count = vendor.get("success_count", 0)
    fail_count = vendor.get("fail_count", 0)
    dispute_count = vendor.get("dispute_count", 0)

    total_count = success_count + fail_count + dispute_count

    score = 100 * (success_count + 3) / (total_count + 6)

    score -= fail_count * 1.5
    score -= dispute_count * 5

    return clamp(score)


def calculate_behavior_score(vendor: Dict[str, Any], transaction: Dict[str, Any]) -> float:
    # const
    INVALID_ADDRESS = -50
    INVALID_SERVICE_ID = -30
    OVERPRICED = -30

    # reject if there are phishing or prompt injection reports
    if vendor.get("has_phishing_report", False):
        return 0

    if vendor.get("has_prompt_injection_report", False):
        return 0

    # calculate behavior score based on transaction details
    score = 100

    receiver_address = transaction.get("receiver_address", "").lower()
    valid_addresses = [
        addr.lower() for addr in vendor.get("receiver_addresses", [])
    ]

    if receiver_address not in valid_addresses:
        score -= INVALID_ADDRESS

    service_id = transaction.get("service_id")
    valid_service_ids = vendor.get("service_ids", [])

    if service_id not in valid_service_ids:
        score -= INVALID_SERVICE_ID

    amount_usd = transaction.get("amount_usd", 0)
    max_reasonable_price = vendor.get("max_reasonable_price_usd", 0)

    if max_reasonable_price > 0 and amount_usd > max_reasonable_price:
        score -= OVERPRICED

    return clamp(score)


def calculate_user_policy_score(vendor: Dict[str, Any], user: Dict[str, Any], transaction: Dict[str, Any]) -> float:
    # const
    AUTO_ALLOW_UNDER = 1
    ANNOUNCE_UNDER = 20
    REQUIRE_APPROVAL_ABOVE = 20

    vendor_id = vendor.get("vendor_id")
    amount_usd = transaction.get("amount_usd", 0)

    budget_policy = user.get("budget_policy", {})
    spending_state = user.get("spending_state", {})

    if vendor_id in user.get("blocked_vendors", []):
        return 0

    daily_total_budget = budget_policy.get("daily_total_budget_usd", 0)
    spent_today = spending_state.get("spent_today_usd", 0)

    if spent_today + amount_usd > daily_total_budget:
        return 0

    per_vendor_budget = budget_policy.get("per_vendor_daily_budget_usd", 0)
    per_vendor_spending_today = spending_state.get("per_vendor_spending_today", {})
    spent_to_this_vendor = per_vendor_spending_today.get(vendor_id, 0)

    if spent_to_this_vendor + amount_usd > per_vendor_budget:
        return 30

    if vendor_id in user.get("trusted_vendors", []):
        return 100

    return 70


def calculate_trust_score(identity_score: float, reputation_score: float, behavior_score: float, user_policy_score: float) -> float:
    # calculate overall trust score with weighted average
    trust_score = (
        0.30 * identity_score +
        0.30 * reputation_score +
        0.25 * behavior_score +
        0.15 * user_policy_score
    )

    return clamp(trust_score)


def decide_action(
    trust_score: float,
    vendor: Dict[str, Any],
    user: Dict[str, Any],
    transaction: Dict[str, Any]
) -> str:
    """
    根據 trust_score、預算、黑名單、金額決定最後 action。

    回傳：
    - ALLOW
    - ANNOUNCE
    - REQUIRE_APPROVAL
    - DENY
    """

    vendor_id = vendor.get("vendor_id")
    amount_usd = transaction.get("amount_usd", 0)

    budget_policy = user.get("budget_policy", {})
    spending_state = user.get("spending_state", {})

    if vendor.get("blacklisted", False):
        return "DENY"

    if vendor_id in user.get("blocked_vendors", []):
        return "DENY"

    if vendor.get("has_phishing_report", False):
        return "DENY"

    if vendor.get("has_prompt_injection_report", False):
        return "DENY"

    daily_total_budget = budget_policy.get("daily_total_budget_usd", 0)
    spent_today = spending_state.get("spent_today_usd", 0)

    if spent_today + amount_usd > daily_total_budget:
        return "DENY"

    per_vendor_budget = budget_policy.get("per_vendor_daily_budget_usd", 0)
    per_vendor_spending_today = spending_state.get("per_vendor_spending_today", {})
    spent_to_this_vendor = per_vendor_spending_today.get(vendor_id, 0)

    if spent_to_this_vendor + amount_usd > per_vendor_budget:
        return "REQUIRE_APPROVAL"

    auto_allow_under = budget_policy.get("auto_allow_under_usd", 1)
    announce_under = budget_policy.get("announce_under_usd", 20)
    require_approval_above = budget_policy.get("require_approval_above_usd", 20)

    if trust_score >= 80 and amount_usd <= auto_allow_under:
        return "ALLOW"

    if trust_score >= 60 and amount_usd <= announce_under:
        return "ANNOUNCE"

    if amount_usd >= require_approval_above:
        return "REQUIRE_APPROVAL"

    if trust_score >= 40:
        return "REQUIRE_APPROVAL"

    return "DENY"


def generate_reason_codes(
    vendor: Dict[str, Any],
    user: Dict[str, Any],
    transaction: Dict[str, Any],
    scores: Dict[str, float],
    action: str
) -> List[str]:
    """
    產生簡單 reason codes，方便 demo 時解釋為什麼做這個決策。
    """

    reasons = []

    vendor_id = vendor.get("vendor_id")
    amount_usd = transaction.get("amount_usd", 0)

    budget_policy = user.get("budget_policy", {})
    spending_state = user.get("spending_state", {})

    if vendor.get("blacklisted", False) or vendor_id in user.get("blocked_vendors", []):
        reasons.append("VENDOR_BLOCKED")

    if vendor.get("verified", False):
        reasons.append("VENDOR_VERIFIED")
    else:
        reasons.append("VENDOR_NOT_VERIFIED")

    if vendor_id in user.get("trusted_vendors", []):
        reasons.append("USER_TRUSTED_VENDOR")

    if scores["reputation_score"] >= 80:
        reasons.append("GOOD_REPUTATION_HISTORY")
    elif scores["reputation_score"] < 50:
        reasons.append("LOW_REPUTATION_HISTORY")

    receiver_address = transaction.get("receiver_address", "").lower()
    valid_addresses = [
        addr.lower() for addr in vendor.get("receiver_addresses", [])
    ]

    if receiver_address not in valid_addresses:
        reasons.append("RECEIVER_ADDRESS_MISMATCH")

    service_id = transaction.get("service_id")
    if service_id not in vendor.get("service_ids", []):
        reasons.append("UNKNOWN_SERVICE_ID")

    max_reasonable_price = vendor.get("max_reasonable_price_usd", 0)
    if max_reasonable_price > 0 and amount_usd > max_reasonable_price:
        reasons.append("AMOUNT_EXCEEDS_REASONABLE_PRICE")

    daily_total_budget = budget_policy.get("daily_total_budget_usd", 0)
    spent_today = spending_state.get("spent_today_usd", 0)

    if spent_today + amount_usd > daily_total_budget:
        reasons.append("DAILY_BUDGET_EXCEEDED")

    per_vendor_budget = budget_policy.get("per_vendor_daily_budget_usd", 0)
    spent_to_this_vendor = spending_state.get(
        "per_vendor_spending_today", {}
    ).get(vendor_id, 0)

    if spent_to_this_vendor + amount_usd > per_vendor_budget:
        reasons.append("PER_VENDOR_BUDGET_EXCEEDED")

    if action == "ALLOW":
        reasons.append("LOW_RISK_AUTO_ALLOWED")
    elif action == "ANNOUNCE":
        reasons.append("TRANSACTION_ALLOWED_WITH_NOTIFICATION")
    elif action == "REQUIRE_APPROVAL":
        reasons.append("HUMAN_APPROVAL_REQUIRED")
    elif action == "DENY":
        reasons.append("TRANSACTION_DENIED")

    return reasons


def evaluate_transaction(
    vendor: Dict[str, Any],
    user: Dict[str, Any],
    transaction: Dict[str, Any]
) -> Dict[str, Any]:
    """
    對一筆交易進行完整評估。

    輸入：
    - vendor: vendor.json 中的一筆 vendor
    - user: user.json
    - transaction: 本次交易請求

    輸出：
    - 各項分數
    - trust_score
    - action
    - reason_codes
    """

    identity_score = calculate_identity_score(vendor, user)
    reputation_score = calculate_reputation_score(vendor)
    behavior_score = calculate_behavior_score(vendor, transaction)
    user_policy_score = calculate_user_policy_score(vendor, user, transaction)

    trust_score = calculate_trust_score(
        identity_score,
        reputation_score,
        behavior_score,
        user_policy_score
    )

    action = decide_action(
        trust_score,
        vendor,
        user,
        transaction
    )

    scores = {
        "identity_score": round(identity_score, 2),
        "reputation_score": round(reputation_score, 2),
        "behavior_score": round(behavior_score, 2),
        "user_policy_score": round(user_policy_score, 2),
        "trust_score": round(trust_score, 2)
    }

    reason_codes = generate_reason_codes(
        vendor,
        user,
        transaction,
        scores,
        action
    )

    return {
        "vendor_id": vendor.get("vendor_id"),
        "vendor_name": vendor.get("name"),
        "transaction": {
            "service_id": transaction.get("service_id"),
            "amount_usd": transaction.get("amount_usd"),
            "receiver_address": transaction.get("receiver_address")
        },
        "scores": scores,
        "action": action,
        "reason_codes": reason_codes
    }