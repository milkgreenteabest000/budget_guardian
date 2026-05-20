# src/notification.py

from typing import Any, Dict, List


def format_risk_flags(risk_flags: List[str]) -> str:
    if not risk_flags:
        return "No risk flags."

    return "\n".join(f"- {flag}" for flag in risk_flags)


def format_scores(scores: Dict[str, Any]) -> str:
    return (
        f"Identity     : {scores.get('identity', 0.0)}\n"
        f"Reputation   : {scores.get('reputation', 0.0)}\n"
        f"Behavior     : {scores.get('behavior', 0.0)}\n"
        f"User Policy  : {scores.get('user_policy', 0.0)}"
    )


def format_transaction(transaction: Dict[str, Any]) -> str:
    return (
        f"Transaction ID  : {transaction.get('transaction_id')}\n"
        f"Service ID      : {transaction.get('service_id')}\n"
        f"Amount USD      : {transaction.get('amount_usd')}\n"
        f"Receiver Address: {transaction.get('receiver_address')}\n"
        f"Payment Reason  : {transaction.get('payment_reason')}"
    )


def print_notification_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def notify_allow(result: Dict[str, Any]) -> None:
    print_notification_header("Payment Allowed")

    print("This transaction is allowed automatically.")
    print()
    print(f"User ID     : {result.get('user_id')}")
    print(f"Vendor ID   : {result.get('vendor_id')}")
    print(f"Vendor Name : {result.get('vendor_name')}")
    print(f"Trust Score : {result.get('trust_score')}")
    print()

    print("Scores")
    print("-" * 70)
    print(format_scores(result.get("scores", {})))
    print()

    print("Risk Flags")
    print("-" * 70)
    print(format_risk_flags(result.get("risk_flags", [])))
    print()

    print("Transaction")
    print("-" * 70)
    print(format_transaction(result.get("transaction", {})))


def notify_announce(result: Dict[str, Any]) -> None:
    print_notification_header("Payment Announced")

    print("This transaction is allowed, but the user should be notified.")
    print()
    print(f"User ID     : {result.get('user_id')}")
    print(f"Vendor ID   : {result.get('vendor_id')}")
    print(f"Vendor Name : {result.get('vendor_name')}")
    print(f"Trust Score : {result.get('trust_score')}")
    print()

    print("Scores")
    print("-" * 70)
    print(format_scores(result.get("scores", {})))
    print()

    print("Risk Flags")
    print("-" * 70)
    print(format_risk_flags(result.get("risk_flags", [])))
    print()

    print("Transaction")
    print("-" * 70)
    print(format_transaction(result.get("transaction", {})))


def notify_require_approval(result: Dict[str, Any]) -> None:
    print_notification_header("Approval Required")

    print("This transaction requires manual approval before payment.")
    print()
    print(f"User ID     : {result.get('user_id')}")
    print(f"Vendor ID   : {result.get('vendor_id')}")
    print(f"Vendor Name : {result.get('vendor_name')}")
    print(f"Trust Score : {result.get('trust_score')}")
    print()

    print("Scores")
    print("-" * 70)
    print(format_scores(result.get("scores", {})))
    print()

    print("Risk Flags")
    print("-" * 70)
    print(format_risk_flags(result.get("risk_flags", [])))
    print()

    print("Transaction")
    print("-" * 70)
    print(format_transaction(result.get("transaction", {})))

    print()
    print("Next Step")
    print("-" * 70)
    print(
        "Run admin.py to check pending approvals, "
        "then approve or reject this transaction."
    )


def notify_deny(result: Dict[str, Any]) -> None:
    print_notification_header("Payment Denied")

    print("This transaction is denied.")
    print()
    print(f"User ID     : {result.get('user_id')}")
    print(f"Vendor ID   : {result.get('vendor_id')}")
    print(f"Vendor Name : {result.get('vendor_name')}")
    print(f"Trust Score : {result.get('trust_score')}")
    print()

    print("Scores")
    print("-" * 70)
    print(format_scores(result.get("scores", {})))
    print()

    print("Risk Flags")
    print("-" * 70)
    print(format_risk_flags(result.get("risk_flags", [])))
    print()

    print("Transaction")
    print("-" * 70)
    print(format_transaction(result.get("transaction", {})))


def notify_decision(result: Dict[str, Any]) -> None:
    action = result.get("action")

    if action == "ALLOW":
        notify_allow(result)
    elif action == "ANNOUNCE":
        notify_announce(result)
    elif action == "REQUIRE_APPROVAL":
        notify_require_approval(result)
    elif action == "DENY":
        notify_deny(result)
    else:
        print_notification_header("Unknown Decision")
        print("Unknown action.")
        print(result)