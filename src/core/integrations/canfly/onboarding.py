# 首次安裝／購買：向使用者請求「是否可修改 memory.md」（佔位）。

from __future__ import annotations

from typing import Any


def prompt_md_edit_authorization(agent_id: str, user_id: str | None) -> dict[str, Any]:
    """
    TODO: 觸發 Canfly UI / Skill 流程，請使用者授權修改 memory.md。
    回傳結構之後對齊 Canfly API。
    """
    return {
        "agent_id": agent_id,
        "user_id": user_id,
        "consent_status": "PENDING",
        "message": "PLACEHOLDER: ask user to allow editing memory.md",
    }


def apply_memory_bootstrap_patch(agent_id: str, user_id: str | None) -> dict[str, Any]:
    """
    TODO: consent 通過後，寫入 memory.md 片段（規則、402 行為、呼叫 BG 等）。
    """
    return {
        "agent_id": agent_id,
        "user_id": user_id,
        "patched": False,
        "message": "PLACEHOLDER: patch memory.md after consent",
    }
