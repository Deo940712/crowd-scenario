# part-002 DESIGN

## Goal

讓 CLI 可輸入自訂 metrics（`--metrics '<json>'`），使 `run` 不再只能跑內建 demo
fixtures。並消除 `_metrics_for` 的靜默 fallback（無 fixture 又無 metrics 時應**印警告**，
不靜默回中性值）——這是 library 層已修掉、CLI 層仍殘留的「靜默吞錯」。

## Non-goals

- 不動引擎 / 契約 / 防火牆邏輯（純 CLI 層）。
- 不改 library API（`make_seed` 已對缺 metric fail-fast，CLI 只負責把錯誤轉成乾淨訊息）。
- 不加 `verify --metrics`（先只做 `run`；verify 用 fixture 足夠，避免範圍蔓延）。

## Assumptions

- `make_seed` 已對缺 axis metric raise `ContractError`（part-001 前的硬化），所以
  `--metrics` 給不全會自然報錯，CLI 只需 catch 成乾淨訊息 + 非零退出。
- CLI 的 `_FALLBACK` 表提供每軸中性值，維持「零設定即可 demo」。
- 優先序需明確：使用者顯式輸入 > 內建 fixture > fallback。

## Design Options

- **A. 只加 --metrics，fallback 維持靜默**：最小改動，但沒解決靜默吞錯，違背 HANDOFF
    任務 B 的第二個重點。捨棄。
- **B. --metrics + fallback 印警告（選定）**：加 `--metrics`，重寫 `_metrics_for` 讓
    「用了 fallback」印 stderr 警告；`--metrics` JSON parse 失敗 / 缺 metric → 乾淨錯誤 +
    非零退出（catch `ContractError` 與 `json.JSONDecodeError`）。
- **C. 移除 fallback，無 metrics 一律報錯**：最嚴格，但破壞「零設定 demo」體驗
    （README 範例 `run --symbol 0056` 免 metrics 就能跑）。捨棄。

## Chosen Design

選 **B**。

`_metrics_for(domain, symbol, override)` 新簽名：
1. `override`（來自 `--metrics`，已 parse 成 dict）非 None → 直接回傳。
2. 否則查 `_FIXTURES[domain][symbol]`，命中 → 回傳。
3. 否則 → **印 stderr 警告**（`warning: no fixture/metrics for '<symbol>' in domain
   '<domain>', using neutral fallback`）後回 `_FALLBACK[domain]`。

`cmd_run`（及沿用 `_metrics_for` 的 `cmd_verify`）流程：
- 若有 `--metrics`：`json.loads`；失敗 → 印 `error: --metrics is not valid JSON: ...`
  到 stderr、`return 2`。解析出的須是 `dict[str, number]`（淺驗證）。
- 呼叫 `make_seed`；若 raise `ContractError`（缺 metric 等）→ 印 `error: <msg>`、`return 2`。
- 正常路徑不變。

JSON 輸出：不新增欄位（metrics 是輸入不是輸出；且原始數字**絕不**回顯——防火牆）。

`--metrics` 只加到 `run`。`verify` 不加（見 non-goals），但 `cmd_verify` 也走
`_metrics_for`，其新簽名 `override=None` 對 verify 行為零影響。

## Verification Targets

- Unit：`tests/test_cli.py` 擴充。
- Regression：`pytest -q` 全綠（78 + 新）。
- `ruff check .`。
- 防火牆：`--metrics` 的原始數字不得出現在任何 persona excerpt 或 JSON（沿用既有
  `test_no_raw_metric_number_leaks_into_persona_text` 精神，新增 CLI 版斷言）。

## Unit Test Strategy

新增到 `tests/test_cli.py`：
- `test_run_accepts_custom_metrics`：`--metrics` 有效 JSON → 正常輸出，且 consensus/
  敘事反映該輸入（用一組會產生明確方向的 metrics）。
- `test_run_metrics_override_beats_fixture`：同 symbol 有 fixture，但 `--metrics` 覆寫
  → 結果依 `--metrics`（seed_id 與純 fixture 版不同）。
- `test_run_invalid_metrics_json_clean_error`：壞 JSON → 非零退出 + stderr 有 error，
  無 traceback。
- `test_run_missing_metric_clean_error`：`--metrics` 缺一軸 → 非零退出 + 乾淨錯誤。
- `test_run_fallback_warns_on_unknown_symbol`：無 fixture 無 metrics → 退出 0 但 stderr
  有 warning（capsys 檢查）。
- `test_run_custom_metrics_do_not_leak_raw_numbers`：`--metrics` 的原始數字不出現在
  JSON 輸出字串中。

## Manual QA Strategy

CLI 冒煙（需 `$env:PYTHONPATH='src'`）：
- `run --symbol 0056 --scenario evt --metrics '{"discount_premium":-0.6,"yield":8.5}'`
- `run --symbol XYZ --scenario evt`（無 fixture）→ 應印 warning 仍跑完
- `run --symbol 0056 --scenario evt --metrics '{bad json'` → 乾淨錯誤、非零退出

## Risks

- Windows PowerShell 對 JSON 字串的引號跳脫容易出錯 → 測試用 `main(argv)` 直接傳
  list，繞開 shell 引號問題；README 範例標註引號用法。
- `_metrics_for` 改簽名會被 `cmd_verify` 共用 → 確認 verify 傳 `override=None`，
  行為不變（回歸測試涵蓋）。

## Open Questions

- 是否淺驗證 `--metrics` 值必須是數字？→ 先做最小淺驗證（值非數字時讓 `make_seed` 的
  bucket_fn 自然報錯即可，不過度防禦），由測試決定是否需要更明確訊息。
