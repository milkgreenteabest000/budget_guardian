# Budget Guardian

Budget Guardian 是一個給 AI Agent 的付款治理層（Agent Payment Governance Layer）。

核心目標是：當 Agent 準備付款或遇到 `HTTP 402 Payment Required` 時，先經過授權流程，再決定是否付款，而不是直接花錢。

---

## 這個 repo 現在能做什麼

- 評估一筆付款意圖的風險，回傳 `ALLOW` / `ANNOUNCE` / `REQUIRE_APPROVAL` / `DENY`
- 產出 `trust_score` 與 `risk_flags`
- 對可放行決策產生 EIP-712 `signature`（`ALLOW`、`ANNOUNCE`）
- 提供 HTTP API：`/authorize`、`/verify`、`/health`、`/mock-402`
- 將交易與裁決寫入 SQLite（`data/app.db`）
- 提供人工核准流程（`core.approve`）
- 提供 Canfly demo 流程（entitlement + onboarding + preflight）

---

## 快速開始（本機）

```bash
pip install -e .
copy .env.example .env
python -m core.infra.init_db
```

### 跑核心 CLI

```bash
python -m core.main
python -m core.main transactions/transaction1.json
python -m core.admin
```

### 跑 BGaaS HTTP

```bash
python -m core.integrations.bgaas.http_stub
```

API 預設位址：`http://127.0.0.1:8000`

### 跑 Canfly demo

```bash
python scripts/canfly_demo.py
```

---

## API 摘要

### `POST /authorize`

請求 body（最小）：

```json
{
  "user_id": "user_001",
  "vendor_id": "vendor_001",
  "intent": {
    "service_id": "pdf_summary_v1",
    "amount_usd": 0.8,
    "receiver_address": "0x1111111111111111111111111111111111111111",
    "payment_reason": "Pay for PDF summarization API"
  },
  "force_after_approval": false
}
```

回傳重點欄位：

- `decision`: `ALLOW` / `ANNOUNCE` / `REQUIRE_APPROVAL` / `DENY`
- `trust_score`: 0-100
- `risk_flags`: 風險標籤
- `signature`: EIP-712 簽章（可放行決策才有）
- `transaction_id`: 審計 ID
- `deadline`, `signer_address`

### `POST /verify`

驗簽請求欄位：`transaction_id`、`decision`、`trust_score`、`deadline`、`signature`  
回傳：`{ "valid": true | false }`

### `POST /mock-402`

回傳模擬 `HTTP 402` 與授權提示 header，方便 demo Agent 流程。

### `GET /health`

服務健康檢查。

---

## 決策規則（目前版本）

分數門檻（`src/core/trust/decision.py`）：

- `>= 90`: `ALLOW`
- `>= 70`: `ANNOUNCE`
- `>= 50`: `REQUIRE_APPROVAL`
- `< 50`: `DENY`

並會由 `risk_flags` 覆寫，例如：

- 直接 `DENY`：`BLACKLISTED_VENDOR`、`HAS_PHISHING_REPORT`、`HAS_PROMPT_INJECTION_REPORT`
- 升級到 `REQUIRE_APPROVAL`：`UNKNOWN_RECEIVER_ADDRESS`、`UNKNOWN_SERVICE_ID`、`DAILY_BUDGET_EXCEEDED` 等

---

## 核准流程（REQUIRE_APPROVAL）

1. 先產生 `REQUIRE_APPROVAL` 的交易（會寫入 approvals）
2. 核准：

```bash
python -m core.approve <transaction_id> approve
```

1. 重新授權：

```bash
python -m core.integrations.bgaas.authorize_cli transactions/transaction4.json --after-approval --tx-id <transaction_id>
```

---

## Canfly 上架與部署

這個 repo 採用的概念是：

- `canfly/skill/SKILL.md`: 給 Agent 的行為規範（何時必須呼叫 BG）
- `src/core/integrations/canfly/*`: Canfly 流程骨架（購買、同意、攔截 preflight）
- `src/core/integrations/bgaas/*`: 真正裁決 API

實務上不建議讓 Agent 直接從 GitHub 執行程式；建議把 BGaaS API 部署成後端服務，Agent 只打 API。

---

## 資料存放

- `data/users.json`、`data/vendors.json`: 評分輸入資料（seed）
- `data/canfly_placeholder_state.json`: Canfly 購買與 consent 狀態
- `data/app.db`: 交易、裁決、核准流程審計資料

---

## 專案結構

```text
src/core/
  main.py                         # CLI 入口
  runtime.py                      # 核心流程編排
  approve.py                      # 核准/拒絕 CLI
  trust/                          # 信任分數與裁決
  infra/                          # data loader / DB / settings / notifications
  integrations/
    bgaas/                        # HTTP API、簽章、驗簽
    canfly/                       # entitlement/onboarding/interception/pipeline
    smart_account/                # 後續 Phase 占位
```

---

## Roadmap

- Smart Account plugin 目前仍為後續 phase
- Canfly 目前為 demo 模式，未接真實 billing 與官方 runtime hook
- 生產環境建議改用雲端 DB（例如 Postgres）

