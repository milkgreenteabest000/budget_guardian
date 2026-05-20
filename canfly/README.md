# Canfly 上架資產（佔位）

與整體系統如何接軌請見 **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)**。

此目錄放 **與 Canfly 平台格式對齊** 的說明、Skill 描述、`memory.md` 注入範本等；實際欄位名稱與打包方式以 Canfly 官方文件為準。

## 預期流程（專題敘事）

1. 使用者於 Canfly **購買／啟用** Budget Guardian。
2. **首次**：請使用者授權是否允許修改 `memory.md`（見 `templates/`）。
3. **已購買且已授權**：由 **`core.integrations.canfly`** 的 pipeline 掛 **HTTP／付費攔截** 與 **BG API**（實作 TODO）。

## 子目錄

| 路徑 | 用途 |
|------|------|
| `skill/SKILL.md` | Skill 簡介與行為說明（佔位） |
| `templates/memory_injection_placeholder.md` | consent 通過後欲寫入 memory 的片段範本（佔位） |

Python 執行邏輯在 **`src/core/`**（套件 **`core`**）。
