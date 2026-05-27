"""EIP-712 簽章與驗簽（Budget Guardian Authorization）。"""

from __future__ import annotations

import time
from typing import Any

from eth_account import Account
from eth_account.messages import encode_typed_data

from ...infra.settings import get_settings
from ...trust import ALLOW, ANNOUNCE, DENY, REQUIRE_APPROVAL

# 僅 ALLOW / ANNOUNCE 可簽可執行付款 token；REQUIRE_APPROVAL 不簽；DENY 不簽。
SIGNABLE_DECISIONS = {ALLOW, ANNOUNCE}


def _domain() -> dict[str, Any]:
    s = get_settings()
    return {
        "name": s["eip712_domain_name"],
        "version": s["eip712_domain_version"],
        "chainId": s["eip712_chain_id"],
        "verifyingContract": s["eip712_verifying_contract"],
    }


def _authorization_types() -> dict[str, list[dict[str, str]]]:
    return {
        "Authorization": [
            {"name": "transactionId", "type": "string"},
            {"name": "decision", "type": "string"},
            {"name": "trustScore", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ],
    }


def build_authorization_message(
    *,
    transaction_id: str,
    decision: str,
    trust_score: float,
    deadline: int | None = None,
) -> dict[str, Any]:
    s = get_settings()
    if deadline is None:
        deadline = int(time.time()) + s["auth_deadline_seconds"]
    return {
        "transactionId": transaction_id,
        "decision": decision,
        "trustScore": int(round(trust_score * 100)),
        "deadline": deadline,
    }


def sign_authorization(
    *,
    transaction_id: str,
    decision: str,
    trust_score: float,
    deadline: int | None = None,
) -> tuple[str | None, str | None, int | None]:
    """
    回傳 (signature_hex, signer_address, deadline)。
    不可簽的 decision 回傳 (None, None, deadline)。
    """
    if decision not in SIGNABLE_DECISIONS:
        s = get_settings()
        dl = deadline or int(time.time()) + s["auth_deadline_seconds"]
        return None, None, dl

    private_key = get_settings().get("signer_private_key")
    if not private_key:
        return None, None, None

    message = build_authorization_message(
        transaction_id=transaction_id,
        decision=decision,
        trust_score=trust_score,
        deadline=deadline,
    )
    dl = message["deadline"]

    structured = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **_authorization_types(),
        },
        "primaryType": "Authorization",
        "domain": _domain(),
        "message": message,
    }

    signable = encode_typed_data(full_message=structured)
    account = Account.from_key(private_key)
    signed = account.sign_message(signable)
    return signed.signature.hex(), account.address, dl


def verify_authorization(
    *,
    transaction_id: str,
    decision: str,
    trust_score: float,
    deadline: int,
    signature: str,
) -> bool:
    if decision not in SIGNABLE_DECISIONS:
        return False
    if int(time.time()) > deadline:
        return False

    private_key = get_settings().get("signer_private_key")
    if not private_key:
        return False

    message = build_authorization_message(
        transaction_id=transaction_id,
        decision=decision,
        trust_score=trust_score,
        deadline=deadline,
    )
    structured = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            **_authorization_types(),
        },
        "primaryType": "Authorization",
        "domain": _domain(),
        "message": message,
    }
    signable = encode_typed_data(full_message=structured)
    expected = Account.from_key(private_key).address

    try:
        sig = signature if signature.startswith("0x") else "0x" + signature
        recovered = Account.recover_message(signable, signature=sig)
        return recovered.lower() == expected.lower()
    except Exception:
        return False
