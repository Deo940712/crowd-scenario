"""Property-based invariants (hypothesis): determinism, categorical output, no leak.

These generalise the example-based tests: for a wide space of raw metric inputs the
engine must stay deterministic, emit only the neutral vocabulary, never leak a raw
number into persona text, and keep every persona stance categorical. Runtime deps stay
empty — hypothesis is a dev-only dependency.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from crowdscenario import STOCK_TW, make_seed, run_scenario

# Raw metric values across a realistic-ish range (both axes the stock pack needs).
_finite = st.floats(min_value=-5.0, max_value=15.0, allow_nan=False, allow_infinity=False)
_metrics = st.fixed_dictionaries({"discount_premium": _finite, "yield": _finite})
_modes = st.sampled_from(["hashed", "aggregate"])
_horizons = st.sampled_from(["intraday", "swing", "long"])


@given(metrics=_metrics, mode=_modes, horizon=_horizons)
def test_run_is_deterministic_for_any_input(metrics, mode, horizon):
    def once():
        seed = make_seed("P", metrics, "evt", horizon=horizon, pack=STOCK_TW)
        return run_scenario(seed, consensus_mode=mode)

    a, b = once(), once()
    assert a.crowd_consensus == b.crowd_consensus
    assert a.narrative_md == b.narrative_md
    assert a.persona_samples == b.persona_samples


@given(metrics=_metrics, mode=_modes)
def test_output_is_always_categorical(metrics, mode):
    seed = make_seed("P", metrics, "evt", pack=STOCK_TW)
    result = run_scenario(seed, consensus_mode=mode)
    assert result.crowd_consensus in ("negative", "neutral", "positive")
    for s in result.persona_samples:
        assert s.stance in (-1, 0, 1)


@given(metrics=_metrics)
def test_no_raw_metric_leaks_into_persona_text(metrics):
    seed = make_seed("P", metrics, "evt", pack=STOCK_TW)
    result = run_scenario(seed)
    for s in result.persona_samples:
        for value in metrics.values():
            assert str(value) not in s.excerpt


@given(mode=_modes)
def test_deeper_discount_never_makes_the_crowd_more_bearish(mode):
    # Monotonicity sanity: a deep discount should not push the aggregate crowd MORE
    # negative than a rich premium (same yield). Compare ordinal directions.
    order = {"negative": -1, "neutral": 0, "positive": 1}
    cheap = run_scenario(
        make_seed("P", {"discount_premium": -2.0, "yield": 5.0}, "evt", pack=STOCK_TW),
        consensus_mode=mode,
    )
    rich = run_scenario(
        make_seed("P", {"discount_premium": 2.0, "yield": 5.0}, "evt", pack=STOCK_TW),
        consensus_mode=mode,
    )
    # cheap should be at least as bullish as rich (>= in ordinal terms) under aggregate;
    # hashed direction is dice, so only assert the aggregate monotonicity.
    if mode == "aggregate":
        assert order[cheap.crowd_consensus] >= order[rich.crowd_consensus]
