import json
import sys

from runtime import process_transaction


def load_transaction(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <transaction_json_path>")
        sys.exit(1)

    transaction_path = sys.argv[1]
    transaction = load_transaction(transaction_path)

    result = process_transaction(
        user_id="user_001",
        vendor_id="vendor_001",
        transaction=transaction,
    )

    print(result)