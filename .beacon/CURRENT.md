# CURRENT

Part: part-015
Slice: slice-004
Status: active
Design authority: `.beacon/parts/part-015/DESIGN.md`
TODO source: `.beacon/parts/part-015/TODO.md#part-015-slice-004-full-verification--close`
Work plan: `.omo/plans/definance-crowd-scenario.md` (todo 9)

## Goal

全面驗證 + 歸檔 part-015:pytest/ruff/`python -O`/LSP/三 domain byte-compare/
verify/DeprecationWarning 路徑;寫 verification-report.md;CURRENT 回 planning-only。

## Allowed Scope
- [ ] .beacon/**(歸檔)
- [ ] .omo/evidence/**

## Forbidden Scope
- 任何 src 變更;git push

## Expected Output

全部 gate 綠;三 domain byte-identical;part-015 done;CURRENT planning-only。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-015 -Slice slice-004`
- Regression: 全部 verification target
- Manual QA: 新 shell 新舊參數 + override 路徑

## Current Blockers
None

## Recovery Incident
None
