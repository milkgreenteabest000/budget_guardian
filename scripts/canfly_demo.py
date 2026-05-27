from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.integrations.canfly import entitlement, interception, onboarding, pipeline  # noqa: E402

AGENT = "agent_demo"
USER = "user_001"


def main() -> None:
    print("=== 1) Before purchase ===")
    print(json.dumps(pipeline.run_canfly_agent_gate(AGENT, USER), indent=2, ensure_ascii=False))

    print("\n=== 2) Record purchase ===")
    print(entitlement.record_purchase(AGENT, USER, "budget_guardian_sku"))

    print("\n=== 3) Grant md consent ===")
    print(onboarding.grant_md_consent(AGENT, USER, allowed=True))

    print("\n=== 4) Gate after onboarding ===")
    print(json.dumps(pipeline.run_canfly_agent_gate(AGENT, USER), indent=2, ensure_ascii=False))

    print("\n=== 5) Preflight authorize (BG server on :8000) ===")
    intent = {
        "service_id": "pdf_summary_v1",
        "amount_usd": 0.8,
        "receiver_address": "0x1111111111111111111111111111111111111111",
        "payment_reason": "Pay for PDF summarization API",
    }
    print(
        json.dumps(
            interception.preflight_authorize(
                user_id=USER,
                vendor_id="vendor_001",
                intent=intent,
            ),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
