# CURRENT

Part: part-015
Slice: slice-003
Status: active
Design authority: `.beacon/parts/part-015/DESIGN.md`
TODO source: `.beacon/parts/part-015/TODO.md#part-015-slice-003-docs-de-finance-readmes--docstrings`
Work plan: `.omo/plans/definance-crowd-scenario.md` (todos 7-8)

## Goal

README(中英)主範例改 software_migration 領先(股票退為其一,不刪);
`make_seed` 範例改用 `scenario_label`;shared-core docstring 金融舉例中性化。

## Allowed Scope
- [ ] README.md、README.zh-TW.md
- [ ] src/crowdscenario/contracts.py、seed.py、domains/base.py 的 DOCSTRING(僅文字)

## Forbidden Scope
- 任何程式行為、簽名、欄位;股票範例不得刪除;git push

## Expected Output

兩份 README 第一個可跑範例為 software_migration;docstring 含非金融例;
`pytest -q` 與 `ruff` 不受影響。

## Verification Plan
- UnitTestCore: design-review gate(docs-only,無自動命令)
- Regression: `pytest -q`;`ruff check .`
- Manual QA: README 新首例指令實跑 exit 0

## Current Blockers
None

## Recovery Incident
None
