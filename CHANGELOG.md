# Changelog

All notable changes to this project are documented here. This project adheres to
semantic-ish versioning during 0.x (behavior changes allowed, called out explicitly).

## [Unreleased]

### Structural firewall hardening (part-014)

- `ScenarioSeed.ordinal_context` now rejects non-string / empty values, so a raw number
  cannot be smuggled into a seed even by constructing one directly.
- `PersonaReaction` validates `stance ∈ {-1,0,1}`; `synthetic_population` is hard-wired
  `True` on `CrowdNarrative` and `NarrativeDivergence`.
- `DomainPack` rejects non-finite (`NaN`/`inf`/bool) numerics and out-of-range
  `voice_variants` stance keys, and is **deep-frozen** after validation (a validated pack
  can no longer be mutated into an invalid state).
- CLI `--metrics` rejects non-finite / non-numeric values with a clean exit-2 error;
  `compose_divergence` raises `ContractError` (not `KeyError`) for an out-of-vocabulary
  posture.

### De-finance (part-015) — naming / defaults / docs only, **no behavior or output change**

- **`make_seed` prefers `scenario_label`** (the neutral name). `market_scenario_label` is
  kept as a **deprecated keyword-only alias** that emits a `DeprecationWarning`; passing
  both with different values raises `TypeError`. The emitted `ScenarioSeed` field name is
  unchanged (serialized-schema stability), and the resolved label produces an identical
  seed hash — output is byte-identical.
- **`DomainPack` gains overridable `register` and `intensity_display`** (were hardcoded
  `"zh-TW"` / 溫和·劇烈 in the engine), so a non-Chinese domain can speak its own language.
  The three shipped packs keep the old values by default — byte-identical output.
- READMEs (en + zh) now lead with a **non-finance** domain example (software migration);
  shared-core docstrings are domain-neutral. The engine core was always domain-agnostic;
  the naming and docs now match.

## [0.2.0] — consensus default changed

### Changed (behavior)

- **Default `consensus_mode` is now `aggregate_neutral`** (was `hashed`).
  The crowd *direction* is now the persona majority off a neutral baseline, so it follows
  the ordinal context instead of the seed hash. This is the most explainable and
  semantically consistent model — see the part-008 consensus evaluation
  (`.beacon/done/part-008/consensus-evaluation.md`).
  - Callers that relied on the old default and want the previous direction must now pass
    `consensus_mode="hashed"` explicitly.
  - `hashed` and `aggregate` remain available as explicit options (nothing removed).
  - Persona `stance` samples and consensus may differ from 0.1.0 for callers that did not
    pass a mode; the emitted artifact shape and firewall guarantees are unchanged.

### Added

- `aggregate_neutral` consensus mode (promoted from experimental in part-008).
- `--consensus-mode aggregate_neutral` in the CLI (now the default).

## [0.1.0] — initial release

- Deterministic, firewalled, domain-pluggable crowd-scenario rehearsal engine.
- `STOCK_TW` and `PRODUCT_LAUNCH` domain packs (a `SOFTWARE_MIGRATION` pack shipped later).
- `hashed` (default) and `aggregate` consensus modes.
- `DeterministicNarrator` + `FusionNarrator` (firewall-screened).
- CLI: `run` / `verify`, `--metrics`, `--sweep`, `--consensus-mode`.
- Adversarially validated firewall scanner; property-based tests.
