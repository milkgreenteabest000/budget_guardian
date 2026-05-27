"""FastAPI BGaaS：/authorize、/verify、/health、mock-402。"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .authorize import authorize_payment_intent
from .eip712 import verify_authorization
from .types import PaymentIntentPayload


class AuthorizeRequest(BaseModel):
    user_id: str = "user_001"
    vendor_id: str = "vendor_001"
    intent: dict[str, Any]
    force_after_approval: bool = False


class VerifyRequest(BaseModel):
    transaction_id: str
    decision: str
    trust_score: float
    deadline: int
    signature: str


def create_http_app() -> FastAPI:
    app = FastAPI(title="Budget Guardian BGaaS", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/authorize")
    def authorize(body: AuthorizeRequest) -> dict[str, Any]:
        intent: PaymentIntentPayload = body.intent  # type: ignore[assignment]
        try:
            return dict(
                authorize_payment_intent(
                    intent,
                    user_id=body.user_id,
                    vendor_id=body.vendor_id,
                    force_after_approval=body.force_after_approval,
                )
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/verify")
    def verify(body: VerifyRequest) -> dict[str, bool]:
        valid = verify_authorization(
            transaction_id=body.transaction_id,
            decision=body.decision,
            trust_score=body.trust_score,
            deadline=body.deadline,
            signature=body.signature,
        )
        return {"valid": valid}

    @app.post("/mock-402")
    def mock_402() -> dict[str, Any]:
        return {
            "status": 402,
            "detail": "Payment Required",
            "headers": {
                "WWW-Authenticate": 'Bearer realm="budget-guardian", authorize_uri="/authorize"',
                "X-Budget-Guard-Authorize": "POST /authorize",
            },
            "body_hint": {
                "user_id": "user_001",
                "vendor_id": "vendor_001",
                "intent": {
                    "service_id": "pdf_summary_v1",
                    "amount_usd": 0.8,
                    "receiver_address": "0x1111111111111111111111111111111111111111",
                    "payment_reason": "Pay for PDF summarization API",
                },
            },
        }

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(
        "core.integrations.bgaas.http_stub:create_http_app",
        factory=True,
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
