# DONE — part-001 / slice-002: Wire --consensus-mode into CLI

Completed snapshot of the promoted CURRENT for this slice.

## Goal (achieved)

把 `consensus_mode` 接到 CLI `run`，讓使用者可從命令列選 hashed / aggregate，
JSON 輸出反映所選模式。

## What shipped

- `cli.py`：
  - `run` 加 `--consensus-mode {hashed,aggregate}`，預設 `hashed`。
  - `cmd_run` 把 `args.consensus_mode` 傳給 `run_scenario`。
  - JSON 輸出加 `consensus_mode` 欄位。
  - 更新模組 docstring（範例 + 說明）。
- `README.md`：CLI 章節加 aggregate 範例 + `--consensus-mode` 說明。
- `tests/test_cli.py`（新檔）：6 個 CLI 層測試。

## Scope decision

`verify` **不加** `--consensus-mode`：verify 是純決定論檢查，hashed 與 aggregate 各自
都決定論，加旗標只是雜訊。測試 `test_verify_has_no_consensus_mode_flag` 鎖住此決定。

## Verification evidence

- `pytest -q` → **78 passed**（72 + 6 CLI）
- `ruff check .` → All checks passed
- Manual QA:
  - `run --symbol 0056 --scenario 0056_cut` → hashed（預設），`crowd_consensus=positive`
    未變，JSON 含 `consensus_mode: hashed`
  - `run --domain product_launch --symbol redesign --scenario redesign --consensus-mode aggregate`
    → `crowd_consensus=neutral`（跟隨 persona 多數，與 hashed 的 positive 不同）
  - `python -O` 契約冒煙 → enforced

## Test-fixup note (透明記錄)

初版 CLI 測試假設 `price_hike` fixture 為 hashed=positive；實測發現 scenario label
進 seed hash 後該 fixture 兩模式皆 negative（斷言基於錯誤假設，非程式 bug）。改用
`redesign/redesign`（hashed=positive vs aggregate=neutral 明確分歧）並將斷言改為
「net-sign 規則 + 兩模式方向不同」而非寫死骰子值，降低脆弱性。

## Incidents

None.
