# Verification Report — part-002

## slice-001: CLI --metrics with fail-fast + fallback warning

Date: (current session)
Status: PASS

| Target | Command | Result |
| --- | --- | --- |
| Unit + Regression | `pytest -q` | 84 passed (78 + 6 CLI) |
| Lint | `ruff check .` | All checks passed |
| Manual QA (custom metrics) | `run --symbol MYETF --scenario evt --metrics '{...}'` | valid artifact, seed reflects input |
| Manual QA (fallback warning) | `run --symbol NOFIX --scenario evt` | stderr warning + artifact on stdout, exit 0 |
| Manual QA (clean error) | `run --symbol X --scenario evt --metrics '{bad'` | stderr error, no traceback, exit 2 |
| Firewall (no raw leak) | `test_run_custom_metrics_do_not_leak_raw_numbers` | raw -1.5 / 9.0 absent from output |

New tests in `tests/test_cli.py`:
- `test_run_accepts_custom_metrics`
- `test_run_metrics_override_beats_fixture`
- `test_run_invalid_metrics_json_is_clean_error`
- `test_run_missing_metric_is_clean_error`
- `test_run_unknown_symbol_without_metrics_warns_but_runs`
- `test_run_custom_metrics_do_not_leak_raw_numbers`

Scope decision: `verify` intentionally has no `--metrics` (part non-goal); `_metrics_for`
override defaults to None so verify behaviour is unchanged.

---

## PART part-002 — COMPLETE

Single slice done. CLI is now usable with real inputs, not just built-in demo fixtures,
and the silent-fallback gap is closed. Final state:
- `pytest -q` → 84 passed
- `ruff check .` → clean
