# part-001 TODO

Design authority: `.beacon/parts/part-001/DESIGN.md`

## SLICE Map

### part-001-slice-001: Aggregate consensus mode (engine)

Status: done — archived at `.beacon/done/part-001/part-001-slice-001-done-current.md`

Goal:
在 `engine.py` 新增 `consensus_mode` 參數與 `aggregate` 兩階段聚合邏輯，讓明確情境
產生方向正確的群眾共識，`hashed` 預設模式零回歸。

Outcome:
`run_scenario(seed, consensus_mode="aggregate")` 的 `crowd_consensus` 方向與多數 persona
stance 一致；`consensus_mode="hashed"`（預設）輸出與現況 byte-identical。

Candidate scope:
- [ ] `engine.py`：`run_scenario` 加 `consensus_mode: str = "hashed"` 關鍵字參數。
- [ ] `engine.py`：實作兩階段聚合（base_consensus → per-persona stance → 多數決），
      hashed 走原路徑。
- [ ] 決定論：整數門檻比較，必要時 tie-break 用 `seed_hash`，不用內建迭代序。
- [ ] `tests/`：加 `test_hashed_mode_unchanged`（先寫，鎖回歸）。
- [ ] `tests/`：加 aggregate follows-personas / deterministic / balanced-neutral 測試，
      參數化 STOCK_TW + PRODUCT_LAUNCH。

Forbidden scope:
- CLI 接線（屬 slice-002）。
- 改動 `_stance_for` 的 tilt 公式。
- 新增任何數字純量欄位到 emitted artifact。
- 改變 hashed 模式的既有輸出。

Verification target:
- Unit: `pytest tests/test_engine.py -q`（新測試全過）
- Regression: `pytest -q`（既有 62 項全綠）+ hashed byte-stable 決定論回歸腳本
- Manual QA: `run --symbol 0056 --scenario 0056_cut`（hashed 輸出未變）

Done gate:
- aggregate 對「深折價+高息」方向正確、同 seed 決定論、hashed 零回歸；
  `pytest` 全綠、`ruff` clean、`python -O` 契約 enforced。

### part-001-slice-002: Wire --consensus-mode into CLI

Status: done — archived at `.beacon/done/part-001/part-001-slice-002-done-current.md`

Goal:
把 `consensus_mode` 接到 CLI，讓使用者可從命令列選 hashed / aggregate。

Outcome:
`run --consensus-mode aggregate` 可運作，JSON 輸出反映所選模式的共識。

Candidate scope:
- [ ] `cli.py`：`run`（及 `verify` 若適用）加 `--consensus-mode {hashed,aggregate}`，
      預設 hashed。
- [ ] 傳遞到 `run_scenario`；JSON 輸出加 `consensus_mode` 欄位。
- [ ] `tests/`：CLI 層測試（parse + 傳遞）。

Forbidden scope:
- 引擎聚合邏輯（屬 slice-001，須先完成）。
- `--metrics`（屬 part-002）。

Verification target:
- Unit: CLI 層測試通過
- Regression: `pytest -q` 全綠
- Manual QA: `run --symbol 0056 --scenario 0056_cut --consensus-mode aggregate`

Done gate:
- CLI 兩模式皆可跑、預設仍 hashed、`pytest`/`ruff` 綠。

Dependencies: slice-002 依賴 slice-001。
