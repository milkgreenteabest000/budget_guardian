"""CLI：對單一 transaction JSON 呼叫 authorize（含 force_after_approval）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .authorize import authorize_payment_intent
from .types import PaymentIntentPayload


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python -m core.integrations.bgaas.authorize_cli <json> "
            "[--after-approval] [--tx-id <transaction_id>]"
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    args = sys.argv[2:]
    force = "--after-approval" in args
    tx_id = None
    if "--tx-id" in args:
        idx = args.index("--tx-id")
        if idx + 1 < len(args):
            tx_id = args[idx + 1]
    with path.open("r", encoding="utf-8") as f:
        intent: PaymentIntentPayload = json.load(f)
    if tx_id:
        intent["transaction_id"] = tx_id

    result = authorize_payment_intent(
        intent,
        user_id="user_001",
        vendor_id="vendor_001",
        force_after_approval=force,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
