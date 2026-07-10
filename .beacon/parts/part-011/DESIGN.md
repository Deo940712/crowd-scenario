# part-011 DESIGN

Source: Codex review（「漂亮的 comparison UI，例如 horizon/intensity sweep，會讓它
從聰明的技術原型變成很有說服力的作品」）+ 內部評估第四優先「展示」。

## Goal

把 `--sweep` 的 6 格資料變成**一眼看懂的對照畫面**：3 horizon × 2 intensity 網格，
每格顯示 consensus、誰先動、反應鏈摘要；旁欄顯示 persona 分布、divergence、
narrator provenance、firewall 狀態。定位是**產品展示與案例閱讀器**，不是聊天 UI。

## Non-goals

- 不做聊天/對話介面（引擎是排練器，不是助手）。
- 不引入 runtime 依賴到引擎 core（UI 是獨立層，可有自己的依賴，但不污染
  `dependencies = []`）。
- 不做即時資料串接（輸入仍是 metrics JSON / 內建 fixtures / case studies）。
- 不在 UI 引入任何數字評分展示（防火牆延伸到視覺層：顯示類別與敘事，不顯示分數條）。

## Assumptions

- `run --sweep` 已輸出 6 格 JSON（含 consensus/narrative/persona_samples/provenance）。
- UI 消費的是引擎的 JSON 輸出——單向讀取，永不回寫（防火牆語義在 UI 層繼續成立）。
- 目標受眾：看 repo 的技術讀者 + case study 讀者。

## Design Options

- **A. 終端 TUI（rich/textual）**：酷但受眾窄、截圖傳播差。捨棄。
- **B. 靜態 HTML 產生器（選定）**：`python -m crowdscenario.report`（或獨立 script）
    吃 sweep JSON → 產生單檔 self-contained HTML（inline CSS，無 CDN、無 JS 依賴或
    僅 vanilla JS）。可離線開啟、可截圖、可放 GitHub Pages、diff 友善。
- **C. Web app（Flask/FastAPI + 前端）**：維護成本高、偏離 zero-dep 精神最遠。捨棄。

## Chosen Design

選 **B**：靜態 HTML 報告產生器。

版面（單頁）：

```
┌─────────────────────────────────────────────────────────┐
│  crowd-scenario report — {symbol} / {scenario}           │
│  domain: stock_tw   consensus_mode: aggregate            │
├──────────────┬──────────────────┬───────────────────────┤
│              │      mild        │       severe          │
├──────────────┼──────────────────┼───────────────────────┤
│  intraday    │ [bullish] 鏈摘要 │ [bullish] 鏈摘要(4步) │
│  swing       │ [neutral] …      │ …                     │
│  long        │ [bearish] …      │ …                     │
├──────────────┴──────────────────┴───────────────────────┤
│  Persona 分布（各格 stance 以顏色標記，非數字條）         │
│  Divergence vs your posture: HIGH → storylines           │
│  Provenance: narrator=deterministic, schema=1            │
│  Firewall: structural contract + scanner (defense-in-depth)│
│  免責：合成排練、非預測、不可回寫決策                     │
└─────────────────────────────────────────────────────────┘
```

實作要點：
- 產生器放 `tools/report.py` 或 `src/crowdscenario/report.py`（若進 package 則仍
  stdlib-only：字串模板即可，不需模板引擎）。
- 輸入：`run --sweep` 的 JSON（stdin 或檔案）＋可選 `--posture` 產 divergence 區塊。
- 輸出：單一 `report.html`。
- persona stance 用顏色/圖示表示類別（紅/灰/綠），**不畫數字條**（視覺層防火牆）。
- 免責聲明固定在頁尾，不可關閉。

## Verification Targets

- Unit：產生器對固定 sweep JSON 產出決定論 HTML（byte-stable）。
- HTML 含 6 格、免責文字、無原始 metric 數字。
- `pytest -q` 全綠、`ruff` clean。
- Manual QA：瀏覽器開啟截圖，肉眼檢查版面與 CJK 顯示。

## Unit Test Strategy

- `test_report_is_deterministic`：同 JSON → byte-identical HTML。
- `test_report_contains_all_six_cells`。
- `test_report_has_disclaimer_and_no_raw_numbers`：免責在、輸入的 raw metrics 不在。
- `test_report_renders_divergence_when_posture_given`。

## Manual QA Strategy

- 對 CASE A/B/C（part-010）各產一份報告，瀏覽器目視：版面、配色可讀性、CJK 無亂碼。
- 手機寬度粗略檢查（單欄 fallback 可接受）。

## Risks

- HTML 內嵌敘事含使用者可控文字 → **必須 HTML-escape**（防 XSS；narrative 來自引擎但
  scenario label 來自使用者輸入）。
- 顏色語義（紅漲綠跌 vs 綠漲紅跌）台美相反 → 用明確文字標籤 + 顏色輔助，不只靠色。
- 「report」若進 package 會增加 API 表面 → 傾向 `tools/`（不進 wheel），slice 定案。

## Open Questions

- 進 package（`python -m crowdscenario.report`）或留 `tools/`？→ 傾向 tools/ 起步，
  受歡迎再升格。slice-001 定案。
- 是否順手支援 case_studies 批次產報告？→ 若 part-010 先完成則加一個 `--all-cases`。
