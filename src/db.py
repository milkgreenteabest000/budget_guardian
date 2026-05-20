# src/db.py

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict


DB_PATH = "app.db"


def get_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def save_transaction(
    user_id: str,
    vendor_id: str,
    transaction: Dict[str, Any],
    status: str,
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO transactions (
            transaction_id,
            user_id,
            vendor_id,
            service_id,
            receiver_address,
            amount_usd,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction.get("transaction_id"),
            user_id,
            vendor_id,
            transaction.get("service_id"),
            transaction.get("receiver_address"),
            transaction.get("amount_usd", 0),
            status,
            get_now(),
        ),
    )

    conn.commit()
    conn.close()


def save_decision(
    transaction_id: str,
    decision_result: Dict[str, Any],
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    scores = decision_result.get("scores", {})
    risk_flags = decision_result.get("risk_flags", [])

    cursor.execute(
        """
        INSERT INTO decisions (
            transaction_id,
            trust_score,
            identity_score,
            reputation_score,
            behavior_score,
            user_policy_score,
            action,
            risk_flags,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            transaction_id,
            decision_result.get("trust_score", 0.0),
            scores.get("identity", 0.0),
            scores.get("reputation", 0.0),
            scores.get("behavior", 0.0),
            scores.get("user_policy", 0.0),
            decision_result.get("action"),
            json.dumps(risk_flags),
            get_now(),
        ),
    )

    conn.commit()
    conn.close()


def create_approval(transaction_id: str) -> None:
    now = get_now()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO approvals (
            transaction_id,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            transaction_id,
            "PENDING",
            now,
            now,
        ),
    )

    conn.commit()
    conn.close()