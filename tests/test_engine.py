"""Engine behaviour: per-persona voices, ordinal-driven stance, reaction chain.

Locks the core invariants — for the stock pack AND for any pack:
- personas read the frozen ordinal context by their own sensitivity (no lockstep flip),
- the emitted stance stays categorical (-1|0|1),
- horizon/intensity reshape the chain,
- the whole narrative is deterministic per seed,
- the emitted ``crowd_consensus`` uses the neutral vocabulary; finance display labels
  only appear in the pack-rendered narrative, never as the contract value.
"""

from __future__ import annotations

import pytest

from crowdscenario.domains.product import PRODUCT_LAUNCH
from crowdscenario.domains.stock_tw import STOCK_TW
from crowdscenario.engine import _stance_for, run_scenario
from crowdscenario.seed import make_seed

_CHEAP = {"discount_premium": "deep_discount", "yield": "high"}
_RICH = {"discount_premium": "rich", "yield": "low"}

# Every pack the skeleton tests run against, with a representative fixture per pack.
_PACKS = [
    (STOCK_TW, {"discount_premium": -0.6, "yield": 8.5}, "0056", "0056_cut"),
    (
        PRODUCT_LAUNCH,
        {"price_change": 0.3, "value_delta": -0.4, "switching_cost": 0.3},
        "newfeature",
        "price_hike",
    ),
]


def _seed(scenario="0056_cut", horizon="swing", intensity="mild", metrics=None):
    return make_seed(
        "0056",
        metrics or {"discount_premium": -0.6, "yield": 8.5},
        scenario,
        rng_seed=42,
        horizon=horizon,
        intensity=intensity,
        pack=STOCK_TW,
    )


# --- Stock-pack-specific behaviour (the reference domain) ---


def test_stance_is_always_categorical():
    for s in run_scenario(_seed()).persona_samples:
        assert s.stance in (-1, 0, 1)


def test_all_ten_archetypes_present_and_distinct_excerpts():
    samples = run_scenario(_seed()).persona_samples
    assert {s.archetype_id for s in samples} == set(STOCK_TW.persona_ids)
    assert len({s.excerpt for s in samples}) > 1


def test_ordinal_context_shifts_stance_at_fixed_consensus():
    assert _stance_for("long_term_holder", "negative", _CHEAP) != _stance_for(
        "long_term_holder", "negative", _RICH
    )


def test_momentum_cohort_ignores_fundamentals_at_fixed_consensus():
    for a in ("day_trader", "leveraged_etf_player", "panic_retail", "ptt_dcard_trendwatch"):
        assert _stance_for(a, "positive", _CHEAP) == _stance_for(a, "positive", _RICH)
        assert _stance_for(a, "negative", _CHEAP) == _stance_for(a, "negative", _RICH)


def test_reaction_chain_present_in_narrative():
    md = run_scenario(_seed()).narrative_md
    assert "反應鏈" in md
    assert "1. " in md


def test_horizon_changes_reaction_chain_lead():
    intraday = run_scenario(_seed(horizon="intraday")).narrative_md
    long = run_scenario(_seed(horizon="long")).narrative_md
    assert intraday != long
    assert intraday.split("1. ")[1].split("\n")[0] != long.split("1. ")[1].split("\n")[0]


def test_intensity_changes_tail_framing():
    mild = run_scenario(_seed(intensity="mild")).narrative_md
    severe = run_scenario(_seed(intensity="severe")).narrative_md
    assert mild != severe


def test_stock_narrative_renders_finance_display_labels():
    md = run_scenario(_seed()).narrative_md
    assert any(label in md for label in ("bearish", "neutral", "bullish"))


# --- Pack-agnostic skeleton invariants (must hold for EVERY pack) ---


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_emitted_consensus_is_neutral_vocabulary(pack, metrics, symbol, scenario):
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    assert run_scenario(seed, pack=pack).crowd_consensus in ("negative", "neutral", "positive")


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_roster_matches_pack_and_stance_categorical(pack, metrics, symbol, scenario):
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    samples = run_scenario(seed, pack=pack).persona_samples
    assert {s.archetype_id for s in samples} == set(pack.persona_ids)
    for s in samples:
        assert s.stance in (-1, 0, 1)


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_determinism_full_narrative(pack, metrics, symbol, scenario):
    a = run_scenario(make_seed(symbol, metrics, scenario, pack=pack), pack=pack)
    b = run_scenario(make_seed(symbol, metrics, scenario, pack=pack), pack=pack)
    assert a.crowd_consensus == b.crowd_consensus
    assert a.narrative_md == b.narrative_md
    assert a.persona_samples == b.persona_samples


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_no_raw_metric_number_leaks_into_persona_text(pack, metrics, symbol, scenario):
    # The raw fixture numbers must never appear verbatim in persona excerpts —
    # only their ordinal buckets crossed the firewall.
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    raw_tokens = {str(v) for v in metrics.values()}
    for s in run_scenario(seed, pack=pack).persona_samples:
        for tok in raw_tokens:
            assert tok not in s.excerpt


def test_different_domains_same_label_do_not_collide():
    # domain_id enters the seed hash, so two packs with the same symbol/label/scenario
    # still get distinct seeds (and thus can diverge).
    stock = make_seed("x", {"discount_premium": -0.6, "yield": 8.5}, "evt", pack=STOCK_TW)
    prod = make_seed(
        "x", {"price_change": 0.3, "value_delta": -0.4, "switching_cost": 0.3}, "evt",
        pack=PRODUCT_LAUNCH,
    )
    assert stock.seed_hash != prod.seed_hash


# --- consensus_mode: hashed (default) vs aggregate (part-001) ---


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_hashed_mode_is_the_default_and_unchanged(pack, metrics, symbol, scenario):
    # Regression lock: the default consensus_mode must reproduce the pre-aggregate
    # behaviour byte-for-byte (same consensus + same narrative + same samples).
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    default = run_scenario(seed, pack=pack)
    explicit_hashed = run_scenario(seed, pack=pack, consensus_mode="hashed")
    assert default.crowd_consensus == explicit_hashed.crowd_consensus
    assert default.narrative_md == explicit_hashed.narrative_md
    assert default.persona_samples == explicit_hashed.persona_samples


def test_hashed_stock_consensus_pinned():
    # Golden value: this specific stock seed has always produced 'positive' in hashed
    # mode. Pin it so an accidental change to the hashed path is caught.
    seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
    assert run_scenario(seed).crowd_consensus == "positive"


def test_aggregate_consensus_follows_persona_majority():
    # The PRODUCT fixture is the motivating case: hashed rolls 'positive' but the
    # persona majority is strongly negative (net -6). Aggregate must follow the crowd.
    seed = make_seed(
        "newfeature",
        {"price_change": 0.3, "value_delta": -0.4, "switching_cost": 0.3},
        "price_hike",
        pack=PRODUCT_LAUNCH,
    )
    result = run_scenario(seed, pack=PRODUCT_LAUNCH, consensus_mode="aggregate")
    net = sum(s.stance for s in result.persona_samples)
    assert net < 0
    assert result.crowd_consensus == "negative"


def test_aggregate_consensus_positive_when_majority_pro():
    # Deep-discount + high-yield stock: persona net is +2 (majority pro) -> positive.
    seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
    result = run_scenario(seed, consensus_mode="aggregate")
    net = sum(s.stance for s in result.persona_samples)
    assert net > 0
    assert result.crowd_consensus == "positive"


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_aggregate_consensus_is_deterministic(pack, metrics, symbol, scenario):
    seed_a = make_seed(symbol, metrics, scenario, pack=pack)
    seed_b = make_seed(symbol, metrics, scenario, pack=pack)
    a = run_scenario(seed_a, pack=pack, consensus_mode="aggregate")
    b = run_scenario(seed_b, pack=pack, consensus_mode="aggregate")
    assert a.crowd_consensus == b.crowd_consensus
    assert a.persona_samples == b.persona_samples
    assert a.narrative_md == b.narrative_md


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_aggregate_consensus_matches_net_sign_rule(pack, metrics, symbol, scenario):
    # The aggregate consensus is a pure function of the persona net: >1 positive,
    # <-1 negative, else neutral. Lock that mapping for every pack.
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    result = run_scenario(seed, pack=pack, consensus_mode="aggregate")
    net = sum(s.stance for s in result.persona_samples)
    expected = "positive" if net > 1 else ("negative" if net < -1 else "neutral")
    assert result.crowd_consensus == expected


def test_unknown_consensus_mode_rejected():
    from crowdscenario.contracts import ContractError

    seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
    with pytest.raises(ContractError):
        run_scenario(seed, consensus_mode="magic")
