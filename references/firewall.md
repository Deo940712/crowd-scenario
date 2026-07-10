# Firewall contract

The crowd layer is a **pure narrative side-rail**. Its safety is not "please
remember to be careful" — it is enforced by *what the layer is allowed to read and
output*, and this holds for **every domain pack**, not just the stock one. Five layers:

1. **Type** — `CrowdNarrative` has no price / nav / discount / yield / weight field,
   and carries **no numeric scalar** — only a categorical `crowd_consensus`. By
   type it cannot return a decision-grade number.
   (`src/crowdscenario/contracts.py`)
2. **Input** — the engine reads only a frozen `ScenarioSeed` carrying *bucketed
   ordinal context* (e.g. `discount_premium -> "deep_discount"`). Personas never see
   a raw number, so they cannot echo or recompute an authoritative figure. The seed
   is frozen and exposes no setters. Bucketing happens once, in `make_seed`, via the
   pack's per-axis `bucket_fn`; the raw metric is dropped there.
3. **Flag** — `non_authoritative` is hard-wired `True` (`__post_init__` assert). Same
   for the report-time `NarrativeDivergence`.
4. **Output whitelist** — the only things emitted are: a categorical stance, per-
   persona reaction text, a herding-ordered reaction chain, and (at report time) a
   `LOW | MEDIUM | HIGH` divergence bucket. Any numeric / decision-shaped scalar is
   simply not a field on the contract.
5. **Pack** — a `DomainPack` supplies only *categorical* material (persona ids, voices,
   display labels, bucket labels). `validate_pack` (run in the pack's `__post_init__`)
   refuses any pack that could corrupt the firewall: parallel tables must be keyed by
   exactly the persona roster, each sensitivity tuple must have one weight per axis,
   and `consensus_display` must map to *strings* only — a numeric display value is
   rejected. So a new domain cannot smuggle a scalar back into an emitted artifact.

> Even under prompt-injection, the worst this layer can do is produce a vivid but
> wrong **story** — it is not wired to any decision or calculation, so it causes
> **zero** damage to any computed number or any action.

## Two layers: structural contract vs. text scanner

The five points above are the **structural firewall** — the primary, load-bearing
guarantee. It is enforced by types and shapes: the engine simply has no field to return
a decision-grade scalar and no way to read a raw number, so a leak is impossible *by
construction*, regardless of what any LLM does.

The rule-based text scanner (`scan_violations`, in `narrator/firewall.py`) is a
**second, softer layer** — defense-in-depth for the optional `FusionNarrator` prose. It
is a conservative, deterministic filter, **not a complete semantic safety proof**. It
screens LLM prose for numeric market tokens and order/injection language before that
prose can enter a `CrowdNarrative`, and it errs toward rejecting a clean-but-suspicious
line (the deterministic prose is always a safe fallback).

### Scanner threat model (what it does and does not catch)

Validated by an adversarial corpus (`tests/firewall_corpus/`, driven by
`tests/test_firewall_adversarial.py`):

| # | Threat | Example | Handled? |
|---|---|---|---|
| T1 | character splitting / spacing | `買 進`, `買　進`, `Ｂ Ｕ Ｙ` | ✅ (NFKC + de-space) |
| T2 | fullwidth / homoglyph digits | `目標價 ５０`, `淨值 １５` | ✅ (NFKC fold) |
| T3 | Chinese numerals + unit | `成本五十元`, `百分之八` | ✅ (unit-anchored pattern) |
| T6 | prompt-injection markers | `忽略前述規則…`, `ignore previous…` | ✅ (heuristic markers) |
| T7 | legitimate conditional prose | `這類人格可能想趁機加碼` | ✅ allowed (zero false positive) |
| T4 | **semantic advice, no banned word** | 「現在是很適合採取行動的時候」 | ❌ **known limitation** |
| T5 | **encoded / obfuscated payload** | Base64, homophone code | ❌ **known limitation** |

T4/T5 are **out of reach for a regex scanner** and are documented as such rather than
pretended away. They matter far less than they would elsewhere, because the *structural*
firewall still holds: even if a semantic suggestion slips through the prose, the engine
emitted no scalar and no raw number — the narrative is a story, wired to nothing.

## Categorical vocabulary, domain display

The emitted `crowd_consensus` uses a domain-neutral vocabulary
(`negative | neutral | positive`). Each pack maps it to its own display labels via
`consensus_display` (stock → bearish/neutral/bullish; product → oppose/neutral/
support). The mapping is **display only** — it never re-enters the stance logic, and
the contract value stays the neutral vocabulary. The per-axis `tilt` floats and the
`herding` floats are engine-internal ordering/threshold inputs; they are collapsed to
a categorical stance (`-1|0|+1`) inside the engine and never leave it.

## Where the number stops

If you want to compare the synthetic crowd against your **own** read, you supply the
posture to `compose_divergence(narrative, external_posture)`. If you only have a
numeric score, `posture_from_score(score)` turns it into a categorical posture first
— the number stops there; only the label is diffed. The engine itself never sees
your posture, so it can never tune its output to agree with you.

## Locked by tests

`tests/test_contracts.py` asserts the invariants: non-authoritative by default,
out-of-vocabulary values rejected, **no** `modifier` / `contrarian_modifier` field on
either the narrative or the divergence, and the `validate_pack` invariants (misaligned
parallel tables, sensitivity/axis length mismatch, and non-string display labels are
all rejected). `tests/test_engine.py` adds pack-agnostic checks that run against every
shipped domain: the emitted consensus stays the neutral vocabulary, the roster matches
the pack, and no raw metric number leaks into persona text.
