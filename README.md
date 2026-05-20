# Budget Guardian

買家 Agent 的預算與付款治理：**Canfly 上架（軟攔截）**與 **Smart Account（硬攔截）** 為兩條並行路線；決策核心共用。

## `src/core/` 長怎樣（精簡）

安裝後套件名：**`core`**（路徑 **`src/core/`**）。

| 區塊 | 路徑 | 說明 |
|------|------|------|
| **入口／編排** | `main.py`、`runtime.py` | `main` → `runtime.process_transaction` |
| **信任模組** | **`trust/`** | `trust_score.py`（算分）、`decision.py`（ALLOW…） |
| **底層設施** | **`infra/`** | `paths`、`data_loader`、`db`、`init_db`、`notifications`（占位） |
| **整合占位** | **`integrations/`** | Canfly、BGaaS |

對外：`from core.trust import make_decision, evaluate_trust_score`；`from core import process_transaction`。

### `infra/` 裡各檔一行話

| 檔案 | 用途 |
|------|------|
| `paths.py` | 專案根、`data/` 路徑 |
| `data_loader.py` | 讀 `users.json`、`vendors.json` |
| `db.py` / `init_db.py` | SQLite `data/app.db` |
| `notifications.py` | 裁決後通知／狀態（占位） |

## 安裝與本機指令

```text
pip install -e .
python -m core.infra.init_db
python -m core.main
```

## 文件與上架資產

- [docs/SERVICES.md](docs/SERVICES.md) — 三服務對照  
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 架構細節  
- [canfly/](canfly/) — Canfly 上架文案／模板  
