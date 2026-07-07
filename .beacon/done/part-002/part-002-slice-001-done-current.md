# DONE — part-002 / slice-001: CLI --metrics with fail-fast + fallback warning

Completed snapshot of the promoted CURRENT for this slice.

## Goal (achieved)

`run` 加 `--metrics '<json>'` 自訂輸入；優先序 override > fixture > fallback；
fallback 印 stderr 警告；壞 JSON / 缺 metric → 乾淨錯誤 + 非零退出。

## What shipped

- `cli.py`：
  - `run` 加 `--metrics`（JSON 字串，預設 None）。
  - `_metrics_for(domain, symbol, override=None)`：override > fixture > fallback；
    fallback 走到時印 stderr warning（不再靜默）。
  - `_parse_metrics(raw)`：`json.loads` + 淺驗證（須為 object），壞 JSON raise
    乾淨 `ValueError`。
  - `cmd_run`：try/except 包住 parse + make_seed；`ValueError`/`ContractError` →
    印 `error: <msg>` 到 stderr、`return 2`。
  - 模組 docstring 更新。
- `README.md`：CLI 章節加 `--metrics` 範例 + 說明。
- `tests/test_cli.py`：6 個新測試。

## Firewall compliance

- `--metrics` 的原始數字**不回顯**：JSON 輸出無原始數字（`test_run_custom_metrics_do_not_leak_raw_numbers`
  斷言 `-1.5` / `9.0` 不在輸出中）。原始數字在 `make_seed` 就 bucket 化。
- 未動引擎 / 契約 / 防火牆邏輯（純 CLI 層）。

## Verification evidence

- `pytest -q` → **84 passed**（78 + 6 CLI）
- `ruff check .` → All checks passed
- Manual QA:
  - `run --symbol MYETF --scenario evt --metrics '{"discount_premium":-0.6,"yield":8.5}'`
    → 正常輸出，seed_id=seed_MYETF_..., crowd_consensus=negative（反映輸入）
  - `run --symbol NOFIX --scenario evt`（無 fixture 無 metrics）
    → stderr 印 warning、stdout 仍產出 artifact、exit 0
  - `run --symbol X --scenario evt --metrics '{bad'`
    → stderr `error: --metrics is not valid JSON: ...`、無 traceback、exit 2

## Scope decision

`verify` **不加** `--metrics`（part non-goal）。`_metrics_for` 新增的 `override` 參數
預設 None，故 `cmd_verify` 沿用時行為完全不變（既有 verify 測試/QA 未受影響）。

## Incidents

None.
