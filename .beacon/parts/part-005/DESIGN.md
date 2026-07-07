# part-005 DESIGN

Source: BACKLOG backlog-004 (test-gap / docs)

## Goal

提供「如何安全地把真實輿情/市場分數餵進 bucket 軸」的 worked example + 文件，
證明防火牆架構在真實資料流下依然成立（原始分數在 `make_seed` 就 bucket 化、不外洩）。

## Non-goals

- 不接任何真實 API / 網路（引擎必須維持 offline、zero-dep）。
- 不改引擎 / 契約 / 防火牆邏輯（純文件 + 範例 + 測試）。
- 不引入外部資料集依賴。

## Assumptions

- `make_seed(symbol, metrics, ...)` 已接受任意 `dict[str, float]`，缺 metric fail-fast。
- 真實輿情分數（如 PTT 情緒 -1..+1、成交量 z-score）就是「raw metric」，交給 axis 的
    bucket_fn 轉 ordinal；原始數字在 seed 建立時即丟棄。
- 防火牆保證已由既有測試鎖住（raw number 不進 persona text）。

## Design Options

- **A. 只加 README 段落**：最小，但沒有可執行證據。
- **B. README 段落 + examples/ 可執行腳本 + 測試（選定）**：
    - `examples/real_data.py`：示範把「模擬的真實分數來源」（一個回傳 dict 的函式，
      代表你的爬蟲/資料層）餵進 `make_seed` → `run_scenario`，印出 categorical 結果。
      明確註解「原始分數到此為止，只有 bucket 過防火牆」。
    - README 加「Feeding real data」章節，連到範例。
    - 測試斷言範例可跑、且原始分數不出現在輸出（防火牆回歸）。

## Chosen Design

選 **B**。範例用「注入式資料源」模式（與 FusionNarrator 的 ModelFn 注入一致精神）：
使用者提供 `fetch_metrics(symbol) -> dict[str, float]`，範例展示如何接上，但範例自帶
一個 fake fetch（stdlib、離線、決定論），保持 zero-dep 與可測試。

檔案：
- `examples/real_data.py`（新目錄 `examples/`）。
- README「Feeding real data」章節。
- `tests/test_examples.py`：import 並跑範例的核心函式，斷言結果 categorical + 無 raw 洩漏。

## Verification Targets

- Unit：`tests/test_examples.py`（範例可執行、輸出 categorical、無 raw number 洩漏）。
- Regression：`pytest -q` 全綠。
- `ruff check .`（examples/ 也納入 lint）。

## Unit Test Strategy

- `test_example_runs_and_emits_categorical`：跑範例主函式 → consensus ∈ 三類。
- `test_example_does_not_leak_raw_scores`：範例用的原始分數不出現在敘事/persona text。
- `test_example_is_deterministic`：同 fake 輸入 → 同輸出。

## Manual QA Strategy

`python examples/real_data.py`（需 `$env:PYTHONPATH='src'`）→ 肉眼確認輸出合理、
無原始數字。

## Risks

- 範例被誤解為「可預測真實市場」→ 文件明確標註 rehearsal-not-forecast + 條件式。
- `examples/` 進 lint/測試範圍需確認 pyproject 設定（testpaths、ruff）。

## Open Questions

- `examples/` 是否納入 wheel 打包？→ 傾向不納入（只是文件示範），確認 hatch packages
    設定不含 examples。
