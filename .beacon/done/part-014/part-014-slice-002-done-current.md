# DONE — part-014 slice-002: DomainPack immutability + finite validation (domains/base.py)

Goal SATISFIED — a validated `DomainPack` can no longer be mutated back into an invalid
state, and non-finite/bool numerics are rejected at construction.

## What was implemented (TDD, plan todos 6-9)

- `validate_pack`: new `_is_finite_number` helper rejects bool (int subclass) + NaN/inf in
  `Axis.tilt`, `herding`, and every `sensitivity` weight (herding had no per-value check
  before). No range locks — finite-only per plan guardrail.
- `validate_pack`: `voice_variants` stance keys bounded to `{-1, 0, 1}` (bool excluded).
- `Axis.__post_init__`: freezes `tilt` as MappingProxyType.
- `DomainPack.__post_init__` → `_freeze_pack`: deep-freezes `herding`, `display_name`,
  `sensitivity`, `consensus_display`, `horizon_frame`, and the nested `voice` /
  `voice_variants` maps. Annotations updated dict→Mapping.

## Verification Evidence

UnitTestCore command: `pytest tests/test_contracts.py tests/test_engine.py -q`

Automated commands:
- `pytest tests/test_contracts.py tests/test_engine.py tests/test_properties.py -q` → 137 passed
- `pytest -q` → 308 passed (zero regressions; +25 new tests over slice-001's 283)
- `ruff check .` → All checks passed
- `python -O -m pytest tests/test_contracts.py -q` → 70 passed (guards survive -O)
- `lsp_diagnostics(src/)` → 0 diagnostics (no annotation drift)
- Evidence: `.omo/evidence/task-6..9-structural-firewall-hardening.txt`

DETERMINISM PROOF (the load-bearing check for this slice):
- Three-domain `run` output byte-compared vs `.omo/evidence/baseline-*.json` (captured
  before any code change): stock_tw / product_launch / software_migration all IDENTICAL.
  Freezing + validation changed NO emitted artifact.

Manual QA:
- item: mutate a shipped pack (STOCK_TW.herding) / construct a pack with NaN herding /
  variant stance 999
- status: passed
- evidence: TypeError on mutation (task-8), ContractError on NaN (task-6) and on stance
  999 (task-7)

TDD red proof: 15 finite/variant-stance tests + 8 freeze tests observed failing first.

Commits:
- 3d9a7ed fix(domains): reject non-finite pack numerics in validate_pack (incl. variant stance bound)
- 7a2e4dc fix(domains): deep-freeze DomainPack mappings after validation

Note: one freeze test asserted TypeError on `.clear()`; corrected to AttributeError
(MappingProxyType has no `clear`) — a test-only fix, item-assignment TypeError is the
canonical read-only proof. Not an implementation defect.

Incidents: none
