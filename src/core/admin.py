# src/admin.py

from infra.db import get_all_transactions, get_pending_approvals


def print_transactions() -> None:
    transactions = get_all_transactions()

    print("=" * 80)
    print("Transactions")
    print("=" * 80)

    if not transactions:
        print("No transactions found.")
        return

    for tx in transactions:
        print(f"Transaction ID : {tx['transaction_id']}")
        print(f"User ID        : {tx['user_id']}")
        print(f"Vendor ID      : {tx['vendor_id']}")
        print(f"Service ID     : {tx['service_id']}")
        print(f"Amount USD     : {tx['amount_usd']}")
        print(f"Status         : {tx['status']}")
        print(f"Created At     : {tx['created_at']}")
        print("-" * 80)


def print_pending_approvals() -> None:
    approvals = get_pending_approvals()

    print("=" * 80)
    print("Pending Approvals")
    print("=" * 80)

    if not approvals:
        print("No pending approvals.")
        return

    for approval in approvals:
        print(f"Approval ID    : {approval['approval_id']}")
        print(f"Transaction ID : {approval['transaction_id']}")
        print(f"Status         : {approval['status']}")
        print(f"Created At     : {approval['created_at']}")
        print(f"Updated At     : {approval['updated_at']}")
        print("-" * 80)


if __name__ == "__main__":
    print_transactions()
    print()
    print_pending_approvals()