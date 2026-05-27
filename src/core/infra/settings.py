"""環境變數與 BG 簽章設定。"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    value = os.environ.get(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


@lru_cache(maxsize=1)
def get_settings() -> dict:
    chain_id = int(_env("BG_EIP712_CHAIN_ID", "31337") or "31337")
    return {
        "signer_private_key": _env("BG_SIGNER_PRIVATE_KEY"),
        "eip712_domain_name": _env("BG_EIP712_DOMAIN_NAME", "BudgetGuardian"),
        "eip712_domain_version": _env("BG_EIP712_DOMAIN_VERSION", "1"),
        "eip712_chain_id": chain_id,
        "eip712_verifying_contract": _env(
            "BG_EIP712_VERIFYING_CONTRACT",
            "0x0000000000000000000000000000000000000000",
        ),
        "bgaas_base_url": _env("BG_API_BASE_URL", "http://127.0.0.1:8000"),
        "auth_deadline_seconds": int(_env("BG_AUTH_DEADLINE_SECONDS", "300") or "300"),
    }
