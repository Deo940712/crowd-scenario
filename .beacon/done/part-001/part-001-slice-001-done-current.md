# DONE — part-001 / slice-001: Aggregate consensus mode (engine)

Completed snapshot of the promoted CURRENT for this slice.

## Goal (achieved)

在 `engine.py` 新增 `consensus_mode` 參數與 `aggregate` 兩階段聚合邏輯，讓明確情境
產生方向正確的群眾共識，`hashed` 預設模式零回歸。

## What shipped

- `engine.py`：
  - 新增 `CONSENSUS_MODES = ("hashed","aggregate")`、`_AGGREGATE_THRESHOLD = 1`、
    `_aggregate_consensus(stances) -> str`（純函式，整數 net-sign，決定論、無純量外洩）。
  - `run_scenario` 新增 `consensus_mode: str = "hashed"` 關鍵字參數；未知值 raise
    `ContractError`。
  - 兩階段：先用 hashed `base_consensus` 算出所有 persona stance（維持個別情境反應），
    aggregate 模式再以 persona 多數 net-sign 覆蓋 emitted consensus。hashed 走原路徑。
- `tests/test_engine.py`：新增 9 個測試（見驗證證據）。

## Firewall / invariant compliance

- 無新增數字純量欄位（aggregate 只回類別字串）。
- hashed 模式輸出 byte-identical（回歸鎖 `test_hashed_mode_is_the_default_and_unchanged`
  + golden `test_hashed_stock_consensus_pinned` 通過）。
- 決定論：整數比較，無 dict/set 迭代序依賴。
- `_stance_for` tilt 公式未動；CLI 未接線（留給 slice-002）。

## Key result (motivating case proven)

PRODUCT `price_hike` 情境：persona net = -6（多數偏空）。
- `hashed`：`positive`（骰子，與群眾矛盾）
- `aggregate`：`negative`（跟隨群眾多數）← 修正了語義矛盾

## Verification evidence

- `pytest -q` → **72 passed**（原 62 + 9 新 − 已知 slice 前 62；實際新增使總數達 72）
- `ruff check .` → All checks passed
- `python -O` 契約冒煙 → enforced（O-mode OK）
- hashed 決定論 + golden：narrative/persona_samples byte-stable、consensus=positive
- CLI 冒煙：`run --symbol 0056 --scenario 0056_cut` 預設 hashed 仍 `positive`（未變）

## Follow-ups

- slice-002：把 `--consensus-mode` 接進 CLI（DESIGN/TODO 已就緒）。

## Incidents

None.
