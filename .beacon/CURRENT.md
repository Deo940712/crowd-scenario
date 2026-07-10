# CURRENT

Part: part-014
Slice: slice-003
Status: active
Design authority: `.beacon/parts/part-014/DESIGN.md`
TODO source: `.beacon/parts/part-014/TODO.md#part-014-slice-003-boundary-hardening-clipy--composerpy`
Work plan: `.omo/plans/structural-firewall-hardening.md` (todos 10-12)

## Goal

CLI `--metrics` 與 `compose_divergence` 對非法輸入回傳一致乾淨錯誤:
`_parse_metrics` 驗證 finite 數值(乾淨 exit 2、無 traceback);`compose_divergence`
前置 `ContractError`(非 KeyError);擴充 `tests/test_cli.py` 整合覆蓋。

## Allowed Scope
- [ ] src/crowdscenario/cli.py
- [ ] src/crowdscenario/composer.py
- [ ] tests/test_cli.py
- [ ] tests/test_composer.py

## Forbidden Scope
- src/crowdscenario/contracts.py、domains/**、engine.py、seed.py
- consensus/schema 變更;bucket/intensity/storylines 數學變更
- 任何 `assert`;git push

## Expected Output

bad metrics(str/null/bool/NaN/Infinity/array/malformed/missing-axis)→ `main([...])` 回 2、
單行 `error:` stderr、空 stdout、無 traceback;`compose_divergence(n,"sideways")` raise
ContractError;`--sweep` 6 cells;unknown symbol fallback 回 0 + warning。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-014 -Slice slice-003`
  (= `pytest tests/test_composer.py tests/test_cli.py -q`)
- Regression: `$env:PYTHONPATH='src'; pytest -q`;`ruff check .`
- Manual QA: `main([run,...,--metrics,<bad>])` in-process 回 2、空 stdout、單行 `error:`

## Current Blockers
None

## Recovery Incident
None
