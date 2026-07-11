# CURRENT

Part: part-015
Slice: slice-001
Status: active
Design authority: `.beacon/parts/part-015/DESIGN.md`
TODO source: `.beacon/parts/part-015/TODO.md#part-015-slice-001-scenario_label-rename--alias-seedpy`
Work plan: `.omo/plans/definance-crowd-scenario.md` (todos 2-3)

## Goal

`make_seed` 改用 `scenario_label`(新名優先、第 3 位置參數不變);
`market_scenario_label` 保留為 deprecated **keyword-only** alias(DeprecationWarning);
兩者同給且不同值拋 TypeError;皆缺拋 TypeError。內部呼叫者改用新名。
決定論硬 gate:三 domain byte-identical 於 part-014 基線。

## Allowed Scope
- [ ] src/crowdscenario/seed.py
- [ ] src/crowdscenario/cli.py(僅 make_seed 呼叫參數名)
- [ ] examples/real_data.py(僅參數名)
- [ ] tests/(新增 alias 測試;檔案位置依 repo 慣例)

## Forbidden Scope
- ScenarioSeed 欄位名(contracts.py 的 market_scenario_label 屬性不動)
- engine.py、domains/**、composer.py 的行為
- 任何 `assert`;git push

## Expected Output

新舊參數路徑測試 fail-then-pass;`pytest.warns(DeprecationWarning)` 驗證舊名;
三 domain `run` 輸出 byte-identical 於 `.omo/evidence/baseline-*.json`。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-015 -Slice slice-001`
- Regression: `$env:PYTHONPATH='src'; pytest -q`;`ruff check .`
- Manual QA: `python -c` 新名/舊名/衝突三路徑;byte-compare x3

## Current Blockers
None

## Recovery Incident
None
