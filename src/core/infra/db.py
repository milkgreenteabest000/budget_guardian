# src/core/infra/db.py

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


from .paths import DATA_DIR

DB_PATH = DATA_DIR / "app.db"
DB_PATH_STR = str(DB_PATH)


def get_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_connection_path() -> Path:
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH_STR)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            vendor_id TEXT NOT NULL,
            service_id TEXT,
            receiver_address TEXT,
            amount_usd REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            trust_score REAL NOT NULL,
            identity_score REAL NOT NULL,
            reputation_score REAL NOT NULL,
            behavior_score REAL NOT NULL,
            user_policy_score REAL NOT NULL,
            action TEXT NOT NULL,
            risk_flags TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals (
            approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
        )
        """
    )

    conn.commit()
    conn.close()


def save_transaction(
    user_id: str,
    vendor_id: str,
    transaction: Dict[str, Any],
    status: str,
) -> None:
    transaction_id = transaction.get("transaction_id")

    if not transaction_id:
        raise ValueError("transaction_id is required before saving transaction.")

    conn = get_connection()
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
            transaction_id,
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
    if not transaction_id:
        raise ValueError("transaction_id is required before saving decision.")

    scores = decision_result.get("scores", {})
    risk_flags = decision_result.get("risk_flags", [])

    conn = get_connection()
    cursor = conn.cursor()

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
    if not transaction_id:
        raise ValueError("transaction_id is required before creating approval.")

    now = get_now()

    conn = get_connection()
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


def get_all_transactions() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM transactions
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_transactions_by_user(user_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
        """,
        (transaction_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


def get_all_decisions() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM decisions
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    decisions = []

    for row in rows:
        decision = dict(row)
        decision["risk_flags"] = json.loads(decision.get("risk_flags", "[]"))
        decisions.append(decision)

    return decisions


def get_decision_by_transaction_id(
    transaction_id: str,
) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM decisions
        WHERE transaction_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (transaction_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    decision = dict(row)
    decision["risk_flags"] = json.loads(decision.get("risk_flags", "[]"))

    return decision


def get_approval_by_transaction_id(transaction_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM approvals
        WHERE transaction_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (transaction_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_pending_approvals() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM approvals
        WHERE status = 'PENDING'
        ORDER BY created_at ASC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_approvals() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM approvals
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_transaction_status(
    transaction_id: str,
    status: str,
) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE transactions
        SET status = ?
        WHERE transaction_id = ?
        """,
        (status, transaction_id),
    )

    conn.commit()
    conn.close()


def update_approval_status(
    transaction_id: str,
    status: str,
) -> None:
    if status not in {"APPROVED", "REJECTED"}:
        raise ValueError("approval status must be APPROVED or REJECTED.")

    now = get_now()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE approvals
        SET status = ?, updated_at = ?
        WHERE transaction_id = ?
        """,
        (status, now, transaction_id),
    )

    cursor.execute(
        """
        UPDATE transactions
        SET status = ?
        WHERE transaction_id = ?
        """,
        (status, transaction_id),
    )

    conn.commit()
    conn.close()


def delete_all_records() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM approvals")
    cursor.execute("DELETE FROM decisions")
    cursor.execute("DELETE FROM transactions")

    conn.commit()
    conn.close()