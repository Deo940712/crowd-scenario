# Changelog

All notable changes to this project are documented here. This project adheres to
semantic-ish versioning during 0.x (behavior changes allowed, called out explicitly).

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
- `STOCK_TW` and `PRODUCT_LAUNCH` domain packs.
- `hashed` (default) and `aggregate` consensus modes.
- `DeterministicNarrator` + `FusionNarrator` (firewall-screened).
- CLI: `run` / `verify`, `--metrics`, `--sweep`, `--consensus-mode`.
- Adversarially validated firewall scanner; property-based tests.
