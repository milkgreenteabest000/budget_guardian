import json
from trust_score import evaluate_trust_score


transaction = {
    "service_id": "pdf_summary_v1",
    "amount_usd": 0.8,
    "receiver_address": "0x1111111111111111111111111111111111111111",
    "payment_reason": "Pay for PDF summarization API",
}


result = evaluate_trust_score(
    user_id="user_001",
    vendor_id="vendor_001",
    transaction=transaction,
)

print(json.dumps(result, indent=2, ensure_ascii=False))