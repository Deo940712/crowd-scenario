# DONE — part-014 slice-001: Contract hardening (contracts.py)

Goal SATISFIED — public dataclasses in `contracts.py` can no longer be constructed
in a firewall-violating state.

## What was implemented (TDD, plan todos 3-5)

- `ScenarioSeed.__post_init__`: `ordinal_context` keys AND values must be non-empty
  strings — rejects raw numbers (float/int/bool), empty labels, non-string keys, and
  nested containers. Closes the "raw price rides into the engine" hole.
- `PersonaReaction.__post_init__` (new): `stance ∈ {-1,0,1}` with explicit bool exclusion
  (True/False rejected), `is_synthetic is True`, `archetype_id`/`register` non-empty
  strings, `excerpt` a string.
- `CrowdNarrative.__post_init__` + `NarrativeDivergence.__post_init__`: hardwired
  `synthetic_population is True`, mirroring the existing `non_authoritative` check.

All guards are explicit `raise ContractError` (no `assert`), so they survive `python -O`.

## Verification Evidence

UnitTestCore command: `pytest tests/test_contracts.py -q`

Automated commands:
- `pytest tests/test_contracts.py -q` → 45 passed
- `python -O -m pytest tests/test_contracts.py -q` → 45 passed (guards not stripped by -O)
- `pytest -q` → 283 passed (was 262 baseline + 21 new tests; zero regressions)
- `ruff check .` → All checks passed
- Evidence: `.omo/evidence/task-3..5-structural-firewall-hardening.txt`

Manual QA:
- item: direct construction of a raw-number ScenarioSeed / out-of-range PersonaReaction /
  non-synthetic CrowdNarrative
- status: passed
- evidence: each prints ContractError (task-3/4/5 evidence files; task-5 confirmed under `python -O`)

TDD red proof: new tests observed FAILING before each fix (8 ordinal, 9 persona, 2 synthetic).

Commits:
- 7704bd0 fix(contracts): reject non-string ordinal_context on ScenarioSeed
- f829953 fix(contracts): validate PersonaReaction stance and synthetic flag
- (synthetic_population commit follows in slice close)

Incidents: none
