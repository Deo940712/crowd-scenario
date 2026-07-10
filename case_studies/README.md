# Case studies

Three reproducible, offline case studies that show what the engine is good at **and where
it must not be trusted**. Each is a scenario *rehearsal*, not a forecast or a backtest —
synthetic personas, hand-curated archetypal inputs, no real product/security.

| # | Case | Domain | default consensus | your read → divergence |
| --- | --- | --- | --- | --- |
| A | [ETF 深折價 + 高殖利率](case_a_etf_discount.md) | stock_tw | positive | neutral → MEDIUM |
| B | [產品漲價，價值提升不足](case_b_price_hike.md) | product_launch | negative | positive → HIGH |
| C | [溢價 + 低殖利率的追高](case_c_premium_chase.md) | stock_tw | negative | positive → HIGH |

Cases B and C also double as a live demonstration of why 0.2.0 changed the default
consensus model: on both, the old `hashed` mode rolled `neutral` while the new default
`aggregate_neutral` correctly follows the clearly-negative scenario.

Every case doc ends with a mandatory **"哪裡不能信 (What this CANNOT tell us)"** section.

## Reproduce

```bash
# print a case's key outputs (buckets, per-mode consensus, sweep, divergence)
#   PowerShell:  $env:PYTHONPATH="src;$PWD"; python case_studies/report.py A
#   bash:        PYTHONPATH="src:$PWD" python case_studies/report.py A   # A | B | C

# the tests lock reproducibility + doc/code agreement + limitations section + no raw leak
pytest tests/test_case_studies.py -q
```

These files live in the repo only — they are not shipped in the PyPI wheel.
