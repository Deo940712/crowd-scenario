# CURRENT

Part: part-014
Slice: slice-001
Status: active
Design authority: `.beacon/parts/part-014/DESIGN.md`
TODO source: `.beacon/parts/part-014/TODO.md#part-014-slice-001-contract-hardening-contractspy`
Work plan: `.omo/plans/structural-firewall-hardening.md` (todos 3-5)

## Goal

讓 `contracts.py` 的公開 dataclass 無法在 firewall 違規狀態下被建構:
`ScenarioSeed.ordinal_context` 只能帶 ordinal 字串、`PersonaReaction` 驗證 stance /
synthetic / 字串欄位、`CrowdNarrative` 與 `NarrativeDivergence` 硬鎖 `synthetic_population`。

## Allowed Scope
- [ ] src/crowdscenario/contracts.py
- [ ] tests/test_contracts.py

## Forbidden Scope
- src/crowdscenario/domains/**、cli.py、composer.py、engine.py、seed.py
- 任何 emitted schema 欄位變更、consensus/persona 變更
- 任何 `assert`(必須用 `raise ContractError`)
- git push

## Expected Output

三類違規建構各有先失敗後通過的測試;所有新 guard 用 `ContractError`;
既有合法建構(含 make_seed、engine 產生的 PersonaReaction)不受影響。

## Verification Plan
- UnitTestCore: `.beacon/verification/UnitTestCore.ps1 -Part part-014 -Slice slice-001`
  (= `pytest tests/test_contracts.py -q`)
- Regression: `$env:PYTHONPATH='src'; pytest -q`;`python -O -m pytest tests/test_contracts.py -q`;`ruff check .`
- Manual QA: `python -c` 建構 `ScenarioSeed(ordinal_context={'p':1.5})` / `PersonaReaction(stance=999)` / `CrowdNarrative(synthetic_population=False)` 各印出 ContractError

## Current Blockers
None

## Recovery Incident
None
