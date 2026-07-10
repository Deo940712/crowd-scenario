# part-013 slice-001 — Gate check + migration impact survey

## Gate check (all three satisfied)

1. ✅ part-008 all slices done, archived under `.beacon/done/part-008/`.
2. ✅ `consensus-evaluation.md` recommends a specific default: **`aggregate_neutral`**.
3. ✅ Recommendation is backed by the five criteria (explainability / semantic
   consistency / neutral stability / determinism / no case-specific hack), each with a
   line-by-line rationale in the evaluation report.

→ **Conclusion: EXECUTE the migration** (not a no-op).

## Migration target

`run_scenario(..., consensus_mode="hashed")` → `"aggregate_neutral"`, and the CLI
`--consensus-mode` default likewise. `hashed` and `aggregate` remain explicit options
(no mode removed).

## Impact survey

### Definition points to change (2)

- `src/crowdscenario/engine.py:195` — `consensus_mode: str = "hashed"`
- `src/crowdscenario/cli.py:213` — `--consensus-mode` `default="hashed"`

### Dry-run drift (measured, not guessed)

Temporarily setting the default to `aggregate_neutral` and running the full suite
produced **exactly 3 failures** out of 232 — the blast radius is small because most tests
assert *properties* (determinism, categorical output, no-leak), not a specific default
value:

1. `test_hashed_mode_is_the_default_and_unchanged[pack0]` — asserts default == hashed.
2. `test_hashed_mode_is_the_default_and_unchanged[pack1]` — same.
3. `test_intraday_and_long_leads_are_pinned` — neutral baseline changes persona stances,
   so the reaction-chain leaders shift (the pins were captured under the hashed default).

### Migration classification

| Location | Kind | Action |
| --- | --- | --- |
| engine.py / cli.py default | definition | change to `aggregate_neutral` |
| `test_hashed_mode_is_the_default_and_unchanged` | default-behavior test | rename/retarget: assert default == **aggregate_neutral**; keep a separate explicit-hashed golden |
| `test_intraday_and_long_leads_are_pinned` | reaction-chain pin under old default | re-pin under new default OR pin explicitly with `consensus_mode="hashed"` (it tests ordering, not consensus) |
| `test_default_is_hashed_pinned` (test_engine) | default-record test | update to `test_default_is_aggregate_neutral_pinned` |
| `test_run_defaults_to_hashed_mode` (test_cli) | CLI default test | retarget to aggregate_neutral; keep explicit-hashed CLI test |
| `test_current_modes_pinned_for_evaluation_corpus` | explicit-mode golden | **unchanged** (already passes explicit modes) |
| `test_hashed_stock_consensus_pinned` | explicit-hashed via `run_scenario(seed)` | **must add explicit** `consensus_mode="hashed"` (currently relies on default) |
| examples/real_data.py | already passes `consensus_mode="aggregate"` explicitly | unchanged |
| tools/eval_consensus.py | passes explicit modes | unchanged |
| README.md / README.zh-TW.md | default description + examples | update default wording; example outputs re-checked |
| pyproject.toml + __init__ __version__ | version | bump 0.1.0 → 0.2.0 |
| PUBLISHING.md | mentions version sync | already generic |

### Docs with implicit default output to re-verify

- README "Use it from the CLI" / "Use it from Python" — any narrative/consensus shown
  without a mode now reflects aggregate_neutral. Re-run the shown commands.

## slice-002 execution checklist (derived)

1. engine.py + cli.py default → `aggregate_neutral`.
2. Retarget the 4 default-behavior tests; add explicit `consensus_mode="hashed"` to
   `test_hashed_stock_consensus_pinned` and (if it relies on default) any hashed-golden test.
3. Re-pin `test_intraday_and_long_leads_are_pinned` (or pin it to explicit hashed).
4. Add `test_default_mode_is_aggregate_neutral`.
5. README (en+zh) default wording + re-verified example outputs; CHANGELOG entry.
6. Version bump 0.1.0 → 0.2.0 (pyproject + `__init__.__version__`).
7. `pytest -q` green, `ruff` clean, `python -O` contract, CLI default smoke.
