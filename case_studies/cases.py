"""The three case-study specs (part-010).

Inputs are hand-curated archetypal scenario snapshots — offline and reproducible, NOT
live data and NOT tied to any real product/security. See runner.py for what each field
means; run `python case_studies/report.py` (or the tests) to reproduce every output.
"""

from __future__ import annotations

from case_studies.runner import CaseSpec
from crowdscenario import PRODUCT_LAUNCH, STOCK_TW

# CASE A — high-yield ETF, deep discount after going ex-dividend (a 0056-style setup).
CASE_A = CaseSpec(
    label="CASE A — ETF deep discount + high yield",
    pack=STOCK_TW,
    symbol="etf_a",
    scenario="ex_dividend_discount",
    raw_metrics={"discount_premium": -1.2, "yield": 8.6},
    your_posture="neutral",  # your own read: cautiously neutral
)

# CASE B — SaaS price hike with weak perceived value gain (a price_hike-style setup).
CASE_B = CaseSpec(
    label="CASE B — price hike, weak value gain",
    pack=PRODUCT_LAUNCH,
    symbol="saas_b",
    scenario="price_hike_low_value",
    raw_metrics={"price_change": 0.3, "value_delta": -0.3, "switching_cost": 0.6},
    your_posture="positive",  # a PM who believes the hike is fine -> HIGH divergence
)

# CASE C — hot ETF trading at a premium with a low yield (a chasing/00878-style setup).
CASE_C = CaseSpec(
    label="CASE C — premium + low yield chase",
    pack=STOCK_TW,
    symbol="etf_c",
    scenario="premium_chase",
    raw_metrics={"discount_premium": 1.4, "yield": 3.1},
    your_posture="positive",  # you're tempted to chase -> contrast with the crowd
)

ALL_CASES = (CASE_A, CASE_B, CASE_C)
