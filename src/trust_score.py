# src/trust_score.py

from pathlib import Path
from typing import Any, Dict
import json


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USER_FILE = DATA_DIR / "users.json"
VENDOR_FILE = DATA_DIR / "vendors.json"

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


def load_json(file_path: Path) -> Dict[str, Any]:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_user(user_id: str) -> Dict[str, Any]:
    user = load_json(USER_FILE)

    if user.get("user_id") != user_id:
        raise ValueError(f"User not found: {user_id}")

    return user


def load_vendor(vendor_id: str) -> Dict[str, Any]:
    vendor = load_json(VENDOR_FILE)

    if vendor.get("vendor_id") != vendor_id:
        raise ValueError(f"Vendor not found: {vendor_id}")

    return vendor


def is_blacklisted(user: Dict[str, Any], vendor: Dict[str, Any]) -> bool:
    vendor_id = vendor.get("vendor_id")

    return (
        vendor.get("blacklisted", False)
        or vendor_id in user.get("blocked_vendors", [])
    )


def validate_transaction(
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
) -> bool:
    if not user or not vendor:
        return False

    if transaction.get("amount_usd", 0) <= 0:
        return False

    return True


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
    vendor_id = vendor.get("vendor_id")
    amount_usd = transaction.get("amount_usd", 0)

    budget_policy = user.get("budget_policy", {})
    spending_state = user.get("spending_state", {})

    if is_blacklisted(user, vendor):
        return 0.0

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


def calculate_final_score(
    identity: float,
    reputation: float,
    behavior: float,
    user_policy: float,
) -> float:
    final_score = (
        IDENTITY_WEIGHT * identity
        + REPUTATION_WEIGHT * reputation
        + BEHAVIOR_WEIGHT * behavior
        + USER_POLICY_WEIGHT * user_policy
    )

    return clamp(final_score)


def evaluate_trust_score(
    user_id: str,
    vendor_id: str,
    transaction: Dict[str, Any],
) -> Dict[str, Any]:
    user = load_user(user_id)
    vendor = load_vendor(vendor_id)

    if not validate_transaction(user, vendor, transaction):
        return {
            "user_id": user_id,
            "vendor_id": vendor_id,
            "trust_score": 0.0,
            "scores": {
                "identity": 0.0,
                "reputation": 0.0,
                "behavior": 0.0,
                "user_policy": 0.0,
            },
            "valid": False,
            "reason": "Invalid transaction",
        }

    identity = calculate_identity(user, vendor)
    reputation = calculate_reputation(vendor)
    behavior = calculate_behavior(user, vendor, transaction)
    user_policy = calculate_user_policy(user, vendor, transaction)

    final_score = calculate_final_score(
        identity=identity,
        reputation=reputation,
        behavior=behavior,
        user_policy=user_policy,
    )

    return {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "trust_score": round(final_score, 2),
        "scores": {
            "identity": round(identity, 2),
            "reputation": round(reputation, 2),
            "behavior": round(behavior, 2),
            "user_policy": round(user_policy, 2),
        },
        "valid": True,
    }