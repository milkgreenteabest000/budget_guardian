# Canfly 上架資產說明

**程式邏輯**在 **`src/core/`**（套件 **`core`**），尤其是 **`core.integrations.canfly`**。  
本頁只說明 **為何另有 `canfly/` 目錄**：它放的是給 **Canfly 平台格式**用的文案與模板（Skill、`memory.md` 注入範本等），方便上架／審核與打包；細節架構見 [ARCHITECTURE.md](ARCHITECTURE.md) 第 3–4 節。

## 預期流程（專題敘事）

1. 使用者在 Canfly **購買／啟用** Budget Guardian。
2. **首次**：請使用者授權是否允許修改 `memory.md`（見 `canfly/templates/`）。
3. **已購買且已授權**：由 **`core.integrations.canfly`** 的 pipeline 掛 **HTTP／付費攔截** 與 **BG API**（實作 TODO）。

## `canfly/` 子路徑

| 路徑 | 用途 |
|------|------|
| `canfly/skill/SKILL.md` | Skill 簡介與行為說明（佔位） |
| `canfly/templates/memory_injection_placeholder.md` | consent 通過後欲寫入 memory 的片段範本（佔位） |

實際欄位名稱與打包方式以 Canfly 官方文件為準。
