# AGENTS.md — crowd-scenario

Developer/agent guide for working **on this codebase**. For the runtime persona
policy the engine itself must obey, see `agent/SOUL.md` (authoritative) and its
reviewer mirror `agent/AGENTS.md` — do not confuse those product guardrails with
this dev file.

## What this is

A deterministic, dependency-free (stdlib-only) Python engine that *rehearses* how
10 Taiwan retail-investor archetypes react to an already-decided market event. It
is a **firewalled, non-authoritative narrative side-rail**: it reads only a bucketed
`ScenarioSeed` and emits only a categorical `crowd_consensus ∈ {bearish,neutral,
bullish}` + narrative. Full rationale in `README.md`.

## Commands

```bash
pip install -e ".[dev]"                                   # editable + pytest, ruff
pytest -q                                                 # all tests
pytest tests/test_contracts.py -q                         # firewall invariants only
pytest tests/test_engine.py::<name> -q                    # single test
ruff check .                                              # lint (line-length 100)
python -m crowdscenario run --symbol 0056 --scenario 0056_cut
python -m crowdscenario verify --symbol 0056 --scenario 0056_cut   # determinism check
```

- Requires Python >= 3.10. Zero runtime deps — **do not add any** (`dependencies = []`
  is intentional; keep it stdlib-only).
- `pyproject.toml` sets `pythonpath = ["src"]`, so `pytest` and `python -m crowdscenario`
  work without installing. Source lives under `src/crowdscenario/` (src layout).
- Ruff rules: `E, F, I, B, UP`, target py310. Run `ruff check .` before finishing.

## The firewall is the product — do not break it

These are load-bearing invariants, locked by `tests/test_contracts.py`. Violating any
is a real bug, not a style nit:

- **No numeric scalar may leave the engine.** `CrowdNarrative` / `NarrativeDivergence`
  carry no additive modifier field. Never add `contrarian_modifier`, `modifier`,
  `score`, weight, or any float a caller could sum into a decision.
- **Read-side stays bucketed.** Raw metrics are dropped in `seed.py` (`bucket_*`);
  only ordinal buckets cross into `ScenarioSeed`. Never pass a raw price/NAV/yield
  into the engine or into persona text.
- **Contracts self-validate** via `__post_init__` — using explicit `raise ContractError`,
  **never `assert`** (asserts vanish under `python -O`, which would silently disable the
  firewall). Vocabulary + range checks: `crowd_consensus`/`external_posture` ∈ CONSENSUS,
  `horizon` ∈ HORIZONS, `intensity` ∈ INTENSITIES, `divergence_bucket` ∈
  DIVERGENCE_BUCKETS, `narrative_intensity` ∈ {1,2,3}, `n_personas` == 0 or 20..50,
  `non_authoritative` hard-wired `True`. If you add a vocabulary value, update the tuple in
  `contracts.py` AND the matching test. `validate_pack` uses the same explicit-raise rule.
- **A seed is bound to its domain.** `ScenarioSeed.domain_id` is set by `make_seed` from
  the pack; `run_scenario` raises if `seed.domain_id != pack.domain_id`, so a stock seed
  can never be silently rehearsed against a product pack. `ordinal_context` is deep-frozen
  (`MappingProxyType`) — a frozen dataclass alone would not stop mutating the dict.
- **Bad domain input fails fast.** `make_seed` raises on a missing axis metric (never a
  silent `0.0`); `_stance_for` raises on a bucket absent from `axis.tilt` (never silent
  neutral). CLI demo fallbacks live in `cli.py` only, so the library API never swallows a typo.
- Internal ordinals (`PersonaReaction.stance ∈ {-1,0,+1}`) are labels for ordering
  the narrative chain only — they are thresholded back to categorical before emission.

## Architecture / data flow

Single linear pipeline (`src/crowdscenario/`):

`make_seed` (`seed.py`, raw metrics → bucketed hashed seed) → `run_scenario`
(`engine.py`, the 10 archetypes + stance logic + herding-ordered reaction chain) →
`CrowdNarrative`. Optionally `compose_divergence` (`composer.py`, crowd-vs-caller's-own
posture, **report time only**, never fed back). `cli.py` wires the CLI; `contracts.py`
holds all four frozen dataclasses + vocabulary tuples.

- Determinism comes from `hashlib.sha256(seed.seed_hash)` in `engine._internal_view`
  — same seed ⇒ same consensus. `horizon` + `intensity` feed the hash, so changing a
  rehearsal dimension is a different seed. Keep the engine pure/offline: no network, no
  randomness beyond the hashed seed, no clock.
- `_ARCHETYPES`, `_HERDING`, `_ARCHETYPE_VOICE`, `_ZH_NAME`, `_ARCHETYPE_SENSITIVITY`
  in `engine.py` are parallel tables keyed by the same 10 archetype ids — edit them
  together or a lookup breaks. Persona voice text is zh-TW.

## Reference material

`references/personas.md` (archetype roster) and `references/firewall.md` (the contract)
are the design source of truth for persona/firewall behavior.
