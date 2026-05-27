"""核准或拒絕 REQUIRE_APPROVAL 交易。"""

from __future__ import annotations

import sys

from .infra.db import get_approval_by_transaction_id, update_approval_status


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python -m core.approve <transaction_id> approve|reject")
        sys.exit(1)

    transaction_id = sys.argv[1]
    verb = sys.argv[2].lower()
    if verb not in {"approve", "reject"}:
        print("Second argument must be approve or reject")
        sys.exit(1)

    row = get_approval_by_transaction_id(transaction_id)
    if row is None:
        print(f"No approval record for transaction_id={transaction_id}")
        sys.exit(1)

    status = "APPROVED" if verb == "approve" else "REJECTED"
    update_approval_status(transaction_id, status)
    print(f"Updated {transaction_id} -> {status}")
    if verb == "approve":
        print(
            f"Re-authorize: python -m core.integrations.bgaas.authorize_cli "
            f"<json> --after-approval --tx-id {transaction_id}"
        )


if __name__ == "__main__":
    main()
