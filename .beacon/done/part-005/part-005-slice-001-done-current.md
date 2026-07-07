# DONE — part-005 / slice-001: Real-data worked example + docs

Source: BACKLOG backlog-004.

## Goal (achieved)

提供「如何安全把真實分數餵進 bucket 軸」的可執行範例 + 文件，證明防火牆在真實資料流
下仍成立。

## What shipped

- `examples/real_data.py`（新目錄）：注入式 `fetch_metrics(symbol)`（自帶離線 fake）
  → `make_seed` → `run_scenario`，印 categorical 結果 + buckets，註解防火牆邊界。
- README：「Feeding real data」章節 + 範例連結。
- `tests/test_examples.py`（新檔，importlib 從路徑載入）：3 個測試。

## Firewall / determinism

- 範例的原始數字只活在 local 變數；測試斷言原始值（-0.6/8.5）不出現在敘事/consensus。
- 決定論測試鎖同輸入同輸出。
- examples/ 不進 wheel（`[tool.hatch.build.targets.wheel].packages` 僅 src/crowdscenario）。

## Verification evidence

- `pytest -q` → **98 passed**（95 + 3）
- `ruff check .` → clean（examples/ 也納入 lint）
- Manual QA: `python examples/real_data.py` →
  `[0056] consensus=bullish buckets={...}` / `[0050] consensus=bullish buckets={...}`
  （只顯示 buckets，無原始數字）

New tests:
- `test_example_runs_and_emits_categorical`
- `test_example_does_not_leak_raw_scores`
- `test_example_is_deterministic`

## Incidents

None.
