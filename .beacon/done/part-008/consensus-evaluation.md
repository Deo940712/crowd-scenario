# Consensus-model evaluation (part-008)

Source of matrix: `tools/eval_consensus.py` (deterministic, reproducible; locked by
`tests/test_consensus_eval.py`). **Not a backtest, no accuracy claim** — this measures
semantic consistency, neutral stability, and explainability, per the PART DESIGN.

## The three models

| mode | how direction is decided | hash affects direction? |
| --- | --- | --- |
| `hashed` (current default) | seed hash → consensus | yes (directly) |
| `aggregate` | personas react off a HASHED baseline → majority | yes (indirectly, via baseline) |
| `aggregate_neutral` (experimental, part-008) | personas react off a NEUTRAL baseline → majority | **no** |

## Comparison matrix (fixed case corpus)

| case | intended | hashed | aggregate | aggregate_neutral | net |
| --- | --- | --- | --- | --- | --- |
| stock cheap+hi-yield | positive | positive | positive | positive | +6 |
| stock rich+lo-yield | negative | negative | negative | negative | -6 |
| stock fair+mid-yield | neutral | positive | positive | **neutral** | +0 |
| product hike+low-value | negative | **positive** | negative | negative | -8 |
| product value+flat-price | positive | **negative** | **neutral** | positive | +6 |
| product neutral-mid | neutral | positive | positive | **neutral** | +0 |

(**bold** = the model disagrees with the human reading of the buckets.)

### Summary

| metric | hashed | aggregate | aggregate_neutral |
| --- | --- | --- | --- |
| counter-intuitive rows (directional cases) | 2 | 1 | **0** |
| disagrees with persona majority | 1 | 1 | **0** |
| hash-independence | n/a | ✗ | **✓** |

## Decision against the five criteria (DESIGN §Chosen Design)

1. **Explainability** — `aggregate_neutral` wins. Its direction is always the persona
   net-sign, explainable purely from buckets + sensitivities. `hashed` can only be
   explained as "the hash rolled this"; `aggregate` inherits a hashed tint on its baseline.
2. **Semantic consistency** — `aggregate_neutral` wins (0 counter-intuitive directional
   rows vs 2 for hashed, 1 for aggregate). The motivating rows:
   - `product hike+low-value`: hashed rolls *positive* on a clearly negative scenario.
   - `product value+flat-price`: only neutral emits *positive* on a high-value scenario;
     hashed says negative, aggregate is dragged to neutral by its hashed baseline.
3. **Neutral stability** — `aggregate_neutral` wins. Both mid/fair cases (net 0) come out
   `neutral`; hashed/aggregate polarize them to `positive` on a dice roll.
4. **Determinism & firewall** — all three hold (locked by tests). `aggregate_neutral`
   adds no scalar; hash-independence verified across all cases.
5. **No case-specific hack** — the neutral model is a single uniform rule (neutral
   baseline → net-sign), not per-case branching. Confirmed by the parametrized tests.

## Recommendation → go for a default change (executed under part-013, GATED)

`aggregate_neutral` is the most explainable and most semantically consistent model, and
it is the only one whose direction is independent of the seed hash. It should become the
public default.

**But** default change is a public API behavior change with wide golden drift, so it is
**not executed here** — it flows to **part-013** (evidence-gated migration), whose gate is
now satisfied by this report. part-013 slice-001 should:

- survey every un-moded `run_scenario` call site + doc example (migration impact),
- decide naming: promote `aggregate_neutral` to the default, keeping `hashed` and
  `aggregate` as explicit options,
- bump version (0.1.0 → 0.2.0) and update README/CHANGELOG.

### Open follow-up

- backlog-007 (pack-defined categorical prior) is **not** needed: neutral baseline did
  NOT over-neutralize (directional cases still resolved correctly, net ±6/±8). Close as
  won't-do unless a future domain shows over-neutralization.

## Reproduce

```bash
PYTHONPATH=src python tools/eval_consensus.py     # prints this matrix
pytest tests/test_consensus_eval.py -q            # locks reproducibility
```
