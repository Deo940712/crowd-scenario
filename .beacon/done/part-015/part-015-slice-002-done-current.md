# DONE — part-015 slice-002: pack-overridable register + intensity_display

Goal SATISFIED — the persona register and intensity display words moved from engine
hardcode to overridable `DomainPack` fields; three shipped packs byte-identical.

## What was implemented (TDD, plan todos 4-6)

- domains/base.py: `register: str = "zh-TW"` and `intensity_display: Mapping[str, str]`
  (default {"mild": "溫和", "severe": "劇烈"}); validate_pack checks register is a
  non-empty string and intensity_display covers INTENSITIES with non-empty strings;
  _freeze_pack wraps intensity_display read-only.
- engine.py:241 `register=pack.register` (was "zh-TW"); :261
  `intensity_zh=pack.intensity_display.get(seed.intensity, seed.intensity)` (was the
  hardcoded 劇烈/溫和 ternary).
- Tests: 8 pack-field tests (defaults/override/rejects/frozen) + 3 engine tests
  (override register reaches persona_samples; override words reach narrative; default
  packs pin zh-TW + 劇烈).

## Verification Evidence

UnitTestCore command: `pytest tests/test_engine.py tests/test_contracts.py -q`

Automated commands:
- `pytest -q` → 335 passed (324 + 11 new; zero regressions)
- `ruff check .` → All checks passed
- `python -O -m pytest tests/test_contracts.py -q` → 78 passed
- `lsp_diagnostics(src/)` → 0

DETERMINISM (hard gate): three-domain `run` byte-compared vs part-014 baselines:
stock_tw / product_launch / software_migration all IDENTICAL — defaults reproduce the
exact pre-part-015 output.

TDD red proof: 8 pack tests + 2 engine override tests observed failing first.

Commits:
- feat(domains): add pack-overridable register and intensity_display
- refactor(engine): source register and intensity words from the pack

Incidents: none
