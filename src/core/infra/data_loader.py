from pathlib import Path
from typing import Any, Dict
import json

from .paths import DATA_DIR

USER_FILE = DATA_DIR / "users.json"
VENDOR_FILE = DATA_DIR / "vendors.json"


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
