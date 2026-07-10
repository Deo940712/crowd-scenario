# CURRENT

Part: part-014
Slice: slice-002
Status: active
Design authority: `.beacon/parts/part-014/DESIGN.md`
TODO source: `.beacon/parts/part-014/TODO.md#part-014-slice-002-domainpack-immutability--finite-validation-domainsbasepy`
Work plan: `.omo/plans/structural-firewall-hardening.md` (todos 6-9)

## Goal

讓 `domains/base.py` 的 `DomainPack` 在通過 `validate_pack` 後無法被改壞:
拒絕 tilt/herding/sensitivity 的非 finite 與 bool、限 `voice_variants` stance key ∈
{-1,0,1}、以 `MappingProxyType` 深度凍結所有 pack mapping(含 `Axis.tilt`)。
凍結後三 domain 決定論必須 byte-identical。

## Allowed Scope
- [ ] src/crowdscenario/domains/base.py
- [ ] tests/test_contracts.py
- [ ] tests/test_engine.py（若需佐證讀取路徑）

## Forbidden Scope
- src/crowdscenario/contracts.py、cli.py、composer.py、engine.py、seed.py
- pack 建構點（stock_tw.py / product.py / software.py）
- 任何數值範圍限制（herding∈[0,1] 等）—— 只要求 finite
- 任何 `assert`;git push

## Expected Output

NaN/inf/bool 於三個數值表 raise ContractError;`voice_variants` stance 999 raise;
凍結後 mutation raise TypeError,讀取仍可;三 domain `run` 輸出 byte-identical 於
`.omo/evidence/baseline-*.json`;engine 讀取路徑不受影響。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-014 -Slice slice-002`
  (= `pytest tests/test_contracts.py tests/test_engine.py -q`)
- Regression: `$env:PYTHONPATH='src'; pytest -q`;`ruff check .`;LSP src/ = 0;`python -O -m pytest tests/test_contracts.py -q`
- Manual QA: byte-compare 三 domain run vs `.omo/evidence/baseline-*.json`;`python -c` mutate STOCK_TW.herding 印 TypeError

## Current Blockers
None

## Recovery Incident
None
