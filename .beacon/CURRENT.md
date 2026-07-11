# CURRENT

Part: part-015
Slice: slice-002
Status: active
Design authority: `.beacon/parts/part-015/DESIGN.md`
TODO source: `.beacon/parts/part-015/TODO.md#part-015-slice-002-pack-overridable-register--intensity_display-basepy--enginepy`
Work plan: `.omo/plans/definance-crowd-scenario.md` (todos 4-6)

## Goal

把 `register`("zh-TW")與 intensity 顯示詞(溫和/劇烈)從 engine 硬編碼移到
`DomainPack` 可覆寫欄位;三個現有 pack 不填 → 預設沿舊值。
決定論硬 gate:三 domain byte-identical 於 part-014 基線。

## Allowed Scope
- [ ] src/crowdscenario/domains/base.py(新欄位 + validate + freeze)
- [ ] src/crowdscenario/engine.py(僅 :241 register 與 :261 intensity 來源)
- [ ] tests/test_contracts.py、tests/test_engine.py

## Forbidden Scope
- seed.py、cli.py、composer.py
- 三個 pack 的實際值(stock_tw.py / product.py / software.py 不動)
- EngineFacts 欄位名;任何 `assert`;git push

## Expected Output

pack 預設 register=="zh-TW"、intensity_display=={"mild":"溫和","severe":"劇烈"};
override pack 測試 fail-then-pass;三 domain byte-identical。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-015 -Slice slice-002`
- Regression: `pytest -q`;`ruff check .`;LSP src/ = 0;`python -O -m pytest tests/test_contracts.py -q`
- Manual QA: override pack 驗證;byte-compare x3

## Current Blockers
None

## Recovery Incident
None
