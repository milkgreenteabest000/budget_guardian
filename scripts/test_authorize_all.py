import json
from pathlib import Path

from core.integrations.bgaas.authorize import authorize_payment_intent

for i in range(1, 7):
    p = Path(f"transactions/transaction{i}.json")
    intent = json.loads(p.read_text(encoding="utf-8"))
    r = authorize_payment_intent(intent, user_id="user_001", vendor_id="vendor_001")
    sig = "yes" if r.get("signature") else "no"
    print(f"tx{i}: {r['decision']} score={r['trust_score']:.2f} sig={sig}")
