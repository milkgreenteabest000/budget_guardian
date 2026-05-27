"""啟動程式：讀取 transaction JSON，呼叫 runtime.process_transaction。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .infra.paths import PROJECT_ROOT
from .runtime import process_transaction

DEFAULT_TRANSACTION = PROJECT_ROOT / "transactions" / "transaction1.json"


def load_transaction(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    if len(sys.argv) >= 2:
        transaction_path = Path(sys.argv[1])
    else:
        transaction_path = DEFAULT_TRANSACTION
        print(f"(未指定檔案，使用預設) {transaction_path}", file=sys.stderr)

    transaction = load_transaction(transaction_path)
    result = process_transaction(
        user_id="user_001",
        vendor_id="vendor_001",
        transaction=transaction,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python -m core.main [transaction_json_path]")
        print(f"  預設: {DEFAULT_TRANSACTION}")
        sys.exit(0)
    main()