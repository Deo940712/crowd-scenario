# DONE — part-014 slice-003: Boundary hardening (cli.py + composer.py)

Goal SATISFIED — CLI `--metrics` and `compose_divergence` now reject bad input with a
consistent clean error (exit 2 / ContractError), never a traceback or KeyError.

## What was implemented (TDD, plan todos 10-12)

- `cli.py::_parse_metrics`: validates every value is a finite `int|float` (bool excluded,
  NaN/Infinity rejected via `math.isfinite`), normalised to `float`. Closes the raw
  `TypeError` traceback path (a string/bool/NaN metric previously blew up inside a
  bucket_fn). `cmd_run` already maps `ValueError` → exit 2, so errors stay clean.
- `composer.py::compose_divergence`: guards `external_posture not in CONSENSUS` with a
  `ContractError` BEFORE the internal `_ORDER` lookup, replacing a raw `KeyError` leak.
- `tests/test_cli.py`: added 7 value-validation tests (string/null/bool/NaN/Infinity/
  array/valid). Existing tests already covered malformed-JSON, missing-axis, sweep=6
  cells, and unknown-symbol fallback — todo-12's remaining integration scenarios.

## Verification Evidence

UnitTestCore command: `pytest tests/test_composer.py tests/test_cli.py -q`

Automated commands:
- `pytest tests/test_composer.py tests/test_cli.py -q` → 29 passed
- `pytest -q` → 316 passed (zero regressions; +8 over slice-002's 308)
- `ruff check .` → All checks passed
- Evidence: `.omo/evidence/task-10..12-structural-firewall-hardening.txt`

Manual QA:
- item: `main([run,...,--metrics,<string|NaN|bool>])` and `compose_divergence(n,"sideways")`
- status: passed
- evidence: exit 2 with single `error:` line + empty stdout, no Traceback (task-10);
  ContractError not KeyError (task-11); all in-process via capsys (no shell/subprocess)

TDD red proof: 5 metric-value tests + 1 composer test observed failing first.

Commits:
- e18afb5 fix(cli): validate --metrics values as finite numbers
- ba37a59 fix(composer): raise ContractError for bad external_posture

Incidents: none
