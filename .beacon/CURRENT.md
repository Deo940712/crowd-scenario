# CURRENT

Part: part-014
Slice: slice-004
Status: active
Design authority: `.beacon/parts/part-014/DESIGN.md`
TODO source: `.beacon/parts/part-014/TODO.md#part-014-slice-004-full-verification--docs-calibration`
Work plan: `.omo/plans/structural-firewall-hardening.md` (todos 13-14)

## Goal

全面驗證(pytest/ruff/`python -O`/LSP/determinism/report)+ README 結構性宣稱校準
+ 歸檔 part-014。

## Allowed Scope
- [ ] README.md、README.zh-TW.md(僅在證實不準確時改)
- [ ] src/crowdscenario/contracts.py、domains/base.py docstring(僅校準,不改行為)
- [ ] .beacon/**(歸檔)
- [ ] .omo/evidence/**

## Forbidden Scope
- 任何 src 行為變更;backlog 其他工作;git push

## Expected Output

全部 verification target 綠;三 domain 決定論 byte-identical;claim checklist 記錄;
`verification-report.md` 寫入;PLAN 標 part-014 done;CURRENT 回 planning-only。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-014 -Slice slice-004`
  (= `pytest -q`)
- Regression: `pytest -q`;`ruff check .`;`python -O -m pytest -q`;LSP src/ = 0;決定論 byte-compare;`tools/report.py` 產 HTML exit 0
- Manual QA: 新 shell 實跑 CLI happy+failure

## Current Blockers
None

## Recovery Incident
None
