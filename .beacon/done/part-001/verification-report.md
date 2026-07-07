# Verification Report — part-001

## slice-001: Aggregate consensus mode (engine)

Date: (current session)
Status: PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 72 passed |
| Lint | `ruff check .` | All checks passed |
| Firewall under -O | `python -O` contract smoke | enforced (ContractError raised) |
| hashed determinism | 2× run_scenario byte-compare | narrative_md + persona_samples equal; consensus=positive |
| Manual QA (CLI) | `run --symbol 0056 --scenario 0056_cut` | hashed default unchanged (positive) |
| Semantic fix proven | PRODUCT price_hike hashed vs aggregate | hashed=positive, aggregate=negative (net -6) |

New tests added to `tests/test_engine.py`:
- `test_hashed_mode_is_the_default_and_unchanged` (parametrized × 2 packs)
- `test_hashed_stock_consensus_pinned`
- `test_aggregate_consensus_follows_persona_majority`
- `test_aggregate_consensus_positive_when_majority_pro`
- `test_aggregate_consensus_is_deterministic` (parametrized × 2 packs)
- `test_aggregate_consensus_matches_net_sign_rule` (parametrized × 2 packs)
- `test_unknown_consensus_mode_rejected`

## slice-002: Wire --consensus-mode into CLI

Date: (current session)
Status: PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 78 passed (72 + 6 CLI) |
| Lint | `ruff check .` | All checks passed |
| Manual QA (hashed default) | `run --symbol 0056 --scenario 0056_cut` | positive, consensus_mode=hashed (unchanged) |
| Manual QA (aggregate diverges) | `run --domain product_launch --symbol redesign --scenario redesign --consensus-mode aggregate` | neutral (differs from hashed positive) |
| Firewall under -O | `python -O` contract smoke | enforced |

New file `tests/test_cli.py` (6 tests):
- `test_run_defaults_to_hashed_mode`
- `test_run_accepts_explicit_hashed`
- `test_run_aggregate_mode_follows_net_sign_rule`
- `test_run_mode_changes_only_consensus_not_samples`
- `test_parser_rejects_unknown_consensus_mode`
- `test_verify_has_no_consensus_mode_flag`

Scope decision: `verify` intentionally has no `--consensus-mode` (pure determinism check).

---

## PART part-001 — COMPLETE

Both slices done. Aggregate consensus mode ships in engine + CLI. Final state:
- `pytest -q` → 78 passed
- `ruff check .` → clean
- `python -O` contract → enforced
- hashed mode byte-stable (zero regression); aggregate follows persona majority.
