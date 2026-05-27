"""依裁決結果寄通知／更新狀態。

目前版本：
- 支援真正寄 email
- 依照 user.notification_policy 決定是否通知
- email 優先從 user dict 取得
- 若 user dict 沒有 email，會嘗試從 data/app.db 查詢
- spending_state / approval 狀態仍建議由 runtime.py / db.py 管理

需要環境變數：
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD
- SMTP_FROM_EMAIL

Gmail 範例：
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USERNAME=your_email@gmail.com
set SMTP_PASSWORD=your_app_password
set SMTP_FROM_EMAIL=your_email@gmail.com
"""

from __future__ import annotations

import json
import os
import smtplib
import sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List, Optional


ACTION_ALLOW = "ALLOW"
ACTION_ANNOUNCE = "ANNOUNCE"
ACTION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
ACTION_DENY = "DENY"

DEFAULT_DB_PATH = Path("data/app.db")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_transaction_id(transaction: Dict[str, Any]) -> str:
    return str(transaction.get("transaction_id", "UNKNOWN_TRANSACTION"))


def _get_vendor_name(vendor_id: str, vendor: Dict[str, Any]) -> str:
    return str(vendor.get("name") or vendor_id)


def _get_amount(transaction: Dict[str, Any]) -> float:
    try:
        return float(transaction.get("amount_usd", 0))
    except (TypeError, ValueError):
        return 0.0


def _get_risk_flags(decision_result: Dict[str, Any]) -> List[str]:
    flags = decision_result.get("risk_flags", [])
    if isinstance(flags, list):
        return [str(flag) for flag in flags]
    return []


def _format_risk_flags(risk_flags: List[str]) -> str:
    if not risk_flags:
        return "None"
    return ", ".join(risk_flags)


def _get_email_from_user_dict(user: Dict[str, Any]) -> Optional[str]:
    """優先從目前載入的 user dict 取得 email。"""
    notification_policy = user.get("notification_policy", {})

    if not isinstance(notification_policy, dict):
        return None

    email = notification_policy.get("email")

    if isinstance(email, str) and email.strip():
        return email.strip()

    return None


def _get_email_from_app_db(
    *,
    user_id: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> Optional[str]:
    """
    從 data/app.db 查詢 user email。

    這裡做得比較寬鬆，支援幾種常見 schema：

    1. users table 有 notification_policy 欄位：
       notification_policy = '{"email": "user@example.com", ...}'

    2. users table 有 user_json 欄位：
       user_json = '{"user_id": "...", "notification_policy": {"email": "..."} }'

    3. users table 直接有 email 欄位：
       email = 'user@example.com'

    如果你的 users table 欄位不同，只要改這個 function 即可。
    """
    if not db_path.exists():
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        )

        row = cur.fetchone()
        conn.close()

        if row is None:
            return None

        row_dict = dict(row)

        direct_email = row_dict.get("email")
        if isinstance(direct_email, str) and direct_email.strip():
            return direct_email.strip()

        notification_policy_raw = row_dict.get("notification_policy")
        if isinstance(notification_policy_raw, str) and notification_policy_raw.strip():
            try:
                notification_policy = json.loads(notification_policy_raw)
                if isinstance(notification_policy, dict):
                    email = notification_policy.get("email")
                    if isinstance(email, str) and email.strip():
                        return email.strip()
            except json.JSONDecodeError:
                pass

        user_json_raw = row_dict.get("user_json")
        if isinstance(user_json_raw, str) and user_json_raw.strip():
            try:
                user_obj = json.loads(user_json_raw)
                if isinstance(user_obj, dict):
                    notification_policy = user_obj.get("notification_policy", {})
                    if isinstance(notification_policy, dict):
                        email = notification_policy.get("email")
                        if isinstance(email, str) and email.strip():
                            return email.strip()
            except json.JSONDecodeError:
                pass

        return None

    except sqlite3.Error:
        return None


def _get_recipient_email(
    *,
    user_id: str,
    user: Dict[str, Any],
) -> Optional[str]:
    """先從 user dict 找，找不到再從 data/app.db 找。"""
    email = _get_email_from_user_dict(user)

    if email:
        return email

    return _get_email_from_app_db(user_id=user_id)


def _should_send_email(
    *,
    action: str,
    user: Dict[str, Any],
) -> bool:
    """
    根據 notification_policy 判斷是否寄信。

    你的 users.json 模板格式：

    "notification_policy": {
        "email": "user@example.com",
        "notify_on_announce": true,
        "notify_on_require_approval": true,
        "notify_on_deny": true
    }

    預設：
    - ALLOW 不寄
    - ANNOUNCE 看 notify_on_announce
    - REQUIRE_APPROVAL 看 notify_on_require_approval
    - DENY 看 notify_on_deny
    """
    notification_policy = user.get("notification_policy", {})

    if not isinstance(notification_policy, dict):
        notification_policy = {}

    if action == ACTION_ALLOW:
        return False

    if action == ACTION_ANNOUNCE:
        return bool(notification_policy.get("notify_on_announce", True))

    if action == ACTION_REQUIRE_APPROVAL:
        return bool(notification_policy.get("notify_on_require_approval", True))

    if action == ACTION_DENY:
        return bool(notification_policy.get("notify_on_deny", True))

    return False


def _build_email_subject(
    *,
    action: str,
    transaction: Dict[str, Any],
    vendor_id: str,
    vendor: Dict[str, Any],
) -> str:
    transaction_id = _get_transaction_id(transaction)
    vendor_name = _get_vendor_name(vendor_id, vendor)

    if action == ACTION_ANNOUNCE:
        prefix = "Payment Notice"
    elif action == ACTION_REQUIRE_APPROVAL:
        prefix = "Approval Required"
    elif action == ACTION_DENY:
        prefix = "Payment Denied"
    elif action == ACTION_ALLOW:
        prefix = "Payment Allowed"
    else:
        prefix = "Payment Decision"

    return f"[Budget Guard] {prefix}: {vendor_name} / {transaction_id}"


def _build_email_body(
    *,
    user_id: str,
    vendor_id: str,
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
    decision_result: Dict[str, Any],
) -> str:
    action = str(decision_result.get("action", "UNKNOWN"))
    trust_score = decision_result.get("trust_score", "N/A")
    transaction_id = _get_transaction_id(transaction)
    vendor_name = _get_vendor_name(vendor_id, vendor)
    amount_usd = _get_amount(transaction)
    service_id = transaction.get("service_id", "UNKNOWN_SERVICE")
    receiver_address = transaction.get("receiver_address", "UNKNOWN_RECEIVER")
    payment_reason = transaction.get("payment_reason", "")
    risk_flags = _get_risk_flags(decision_result)

    smart_account = user.get("smart_account", {})
    if not isinstance(smart_account, dict):
        smart_account = {}

    chain_id = smart_account.get("chain_id", "UNKNOWN_CHAIN")
    smart_account_address = smart_account.get("address", "UNKNOWN_SMART_ACCOUNT")

    if action == ACTION_ANNOUNCE:
        summary = "This payment was allowed, but Budget Guard generated a notice for visibility."
    elif action == ACTION_REQUIRE_APPROVAL:
        summary = "This payment requires manual approval before it should proceed."
    elif action == ACTION_DENY:
        summary = "This payment was denied by Budget Guard."
    elif action == ACTION_ALLOW:
        summary = "This payment was allowed."
    else:
        summary = "Budget Guard generated a payment decision."

    lines = [
        "Budget Guard Payment Notification",
        "",
        summary,
        "",
        "==============================",
        "User",
        "==============================",
        f"User ID: {user_id}",
        f"Chain ID: {chain_id}",
        f"Smart Account: {smart_account_address}",
        "",
        "==============================",
        "Transaction",
        "==============================",
        f"Transaction ID: {transaction_id}",
        f"Vendor: {vendor_name} ({vendor_id})",
        f"Service ID: {service_id}",
        f"Amount USD: {amount_usd}",
        f"Receiver Address: {receiver_address}",
    ]

    if payment_reason:
        lines.append(f"Payment Reason: {payment_reason}")

    lines.extend(
        [
            "",
            "==============================",
            "Decision",
            "==============================",
            f"Action: {action}",
            f"Trust Score: {trust_score}",
            f"Risk Flags: {_format_risk_flags(risk_flags)}",
            f"Created At: {_now_iso()}",
        ]
    )

    if action == ACTION_REQUIRE_APPROVAL:
        lines.extend(
            [
                "",
                "Please review this transaction before approving it.",
                "Recommended checks:",
                "- Confirm the vendor is expected.",
                "- Confirm the amount is reasonable.",
                "- Confirm the receiver address is correct.",
                "- Review the risk flags before allowing payment.",
            ]
        )

    elif action == ACTION_DENY:
        lines.extend(
            [
                "",
                "This transaction should not proceed unless the user manually overrides the decision.",
            ]
        )

    return "\n".join(lines)


def _send_email(
    *,
    to_email: str,
    subject: str,
    body: str,
) -> Dict[str, Any]:
    """
    用 SMTP 寄信。

    必要環境變數：
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USERNAME
    - SMTP_PASSWORD
    - SMTP_FROM_EMAIL
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port_raw = os.getenv("SMTP_PORT", "587")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_email = os.getenv("SMTP_FROM_EMAIL") or smtp_username

    missing = []

    if not smtp_host:
        missing.append("SMTP_HOST")
    if not smtp_username:
        missing.append("SMTP_USERNAME")
    if not smtp_password:
        missing.append("SMTP_PASSWORD")
    if not smtp_from_email:
        missing.append("SMTP_FROM_EMAIL")

    if missing:
        return {
            "channel": "email",
            "success": False,
            "to": to_email,
            "error": f"Missing SMTP environment variables: {', '.join(missing)}",
        }

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        return {
            "channel": "email",
            "success": False,
            "to": to_email,
            "error": f"Invalid SMTP_PORT: {smtp_port_raw}",
        }

    message = EmailMessage()
    message["From"] = smtp_from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        return {
            "channel": "email",
            "success": True,
            "to": to_email,
            "subject": subject,
            "note": "Email sent successfully.",
        }

    except Exception as exc:
        return {
            "channel": "email",
            "success": False,
            "to": to_email,
            "subject": subject,
            "error": str(exc),
        }

def apply_decision_side_effects(
    *,
    user_id: str,
    vendor_id: str,
    user: Dict[str, Any],
    vendor: Dict[str, Any],
    transaction: Dict[str, Any],
    decision_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    根據裁決結果寄 email 通知。

    runtime.py 可以維持原本呼叫方式不變：

    apply_decision_side_effects(
        user_id=user_id,
        vendor_id=vendor_id,
        user=user,
        vendor=vendor,
        transaction=transaction,
        decision_result=decision_result,
    )

    回傳格式：
    {
        "user_id": "...",
        "vendor_id": "...",
        "transaction_id": "...",
        "action": "...",
        "should_notify": true,
        "recipient_email": "...",
        "dispatched": true,
        "dispatch_result": {...},
        "created_at": "...",
        "note": "..."
    }
    """
    action = decision_result.get("action")
    action = str(action) if action is not None else "UNKNOWN"

    transaction_id = _get_transaction_id(transaction)

    should_notify = _should_send_email(
        action=action,
        user=user,
    )

    if not should_notify:
        return {
            "user_id": user_id,
            "vendor_id": vendor_id,
            "transaction_id": transaction_id,
            "action": action,
            "should_notify": False,
            "recipient_email": None,
            "dispatched": False,
            "dispatch_result": None,
            "created_at": _now_iso(),
            "note": f"No email notification required for action: {action}",
        }

    recipient_email = _get_recipient_email(
        user_id=user_id,
        user=user,
    )

    if not recipient_email:
        return {
            "user_id": user_id,
            "vendor_id": vendor_id,
            "transaction_id": transaction_id,
            "action": action,
            "should_notify": True,
            "recipient_email": None,
            "dispatched": False,
            "dispatch_result": None,
            "created_at": _now_iso(),
            "note": "Email notification required, but recipient email was not found.",
        }

    subject = _build_email_subject(
        action=action,
        transaction=transaction,
        vendor_id=vendor_id,
        vendor=vendor,
    )

    body = _build_email_body(
        user_id=user_id,
        vendor_id=vendor_id,
        user=user,
        vendor=vendor,
        transaction=transaction,
        decision_result=decision_result,
    )

    dispatch_result = _send_email(
        to_email=recipient_email,
        subject=subject,
        body=body,
    )

    dispatched = bool(dispatch_result.get("success"))

    return {
        "user_id": user_id,
        "vendor_id": vendor_id,
        "transaction_id": transaction_id,
        "action": action,
        "should_notify": True,
        "recipient_email": recipient_email,
        "dispatched": dispatched,
        "dispatch_result": dispatch_result,
        "created_at": _now_iso(),
        "note": "Email sent successfully." if dispatched else "Email notification failed.",
    }
