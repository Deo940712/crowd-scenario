# part-014 Verification Report — Structural Firewall Hardening

## Outcome

All four slices complete. The firewall guarantees README promises are now enforced for
every construction path: firewall-violating objects cannot be built, and a validated
DomainPack cannot be mutated back into an invalid state. All existing legal behaviour is
byte-identical (proven).

## Verification Evidence

UnitTestCore command: `pytest -q` (+ per-slice targets in manifest.json)

Automated commands:
- `pytest -q` → 316 passed (baseline was 262; +54 new tests, zero regressions)
- `ruff check .` → All checks passed
- `python -O -m pytest -q` → 316 passed (all contract/pack guards survive optimize mode;
  no `assert` used)
- `lsp_diagnostics(src/)` → 0 diagnostics (no annotation drift from dict→Mapping)
- `verify` stock_tw + software_migration → full_artifact_stable=True → OK

Determinism (load-bearing):
- Three-domain `run` output byte-compared vs `.omo/evidence/baseline-*.json` captured
  BEFORE any code change: stock_tw / product_launch / software_migration all IDENTICAL,
  re-confirmed after slice-002 (task-9) and in the final sweep (task-13).

Report:
- `tools/report.py` HTML generation from `--sweep` → exit 0, 2871-byte report.

## Manual QA

- item: direct construction of raw-number ScenarioSeed / out-of-range PersonaReaction /
  non-synthetic CrowdNarrative
  status: passed — each prints ContractError (task-3/4/5; task-5 confirmed under `python -O`)
- item: construct pack with NaN herding / variant stance 999 / mutate shipped STOCK_TW.herding
  status: passed — ContractError (task-6/7), TypeError on mutation (task-8)
- item: `main([run,...,--metrics,<string|NaN|bool>])` / `compose_divergence(n,"sideways")`
  status: passed — exit 2 with single `error:` line + empty stdout, no traceback (task-10);
  ContractError not KeyError (task-11)

## What changed

- slice-001 (contracts.py): ScenarioSeed ordinal_context string-only; PersonaReaction
  stance/synthetic/string validation; synthetic_population hard-wired on both emitted
  artifacts.
- slice-002 (domains/base.py): finite-only tilt/herding/sensitivity; voice_variants
  stance-key bound; deep-freeze of all pack + Axis mappings.
- slice-003 (cli.py + composer.py): --metrics finite-value validation (clean exit 2);
  compose_divergence ContractError guard.
- slice-004: full verification + README claim calibration (no doc edit needed — claims
  now accurate/stronger).

## Scope fidelity

Product code touched ONLY: contracts.py, domains/base.py, cli.py, composer.py.
Tests touched ONLY: test_contracts.py, test_composer.py, test_cli.py.
Pre-existing unrelated dirty-worktree files were left untouched (recorded, out of scope).

## Commits

- 8bd1e1b chore(beacon): open part-014
- 7704bd0 / f829953 / 13109fa — slice-001 (contracts)
- 3d9a7ed / 7a2e4dc / f1636f2 — slice-002 (domains)
- e18afb5 / ba37a59 / d648084 — slice-003 (cli/composer)
- (slice-004 close commit follows)

Incidents: none
