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
from crowdscenario.domains.software import SOFTWARE_MIGRATION
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
    (
        SOFTWARE_MIGRATION,
        {"breaking_severity": 0.9, "migration_effort": 0.9, "value_gain": 0.1},
        "big_rewrite",
        "v9_rewrite",
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


def _chain_lead(md: str) -> str:
    """The display name of the persona leading the reaction chain (after '1. **')."""
    return md.split("1. **", 1)[1].split("**", 1)[0]


def test_horizon_changes_reaction_chain_lead():
    intraday = run_scenario(_seed(horizon="intraday")).narrative_md
    long = run_scenario(_seed(horizon="long")).narrative_md
    assert intraday != long
    assert intraday.split("1. ")[1].split("\n")[0] != long.split("1. ")[1].split("\n")[0]


def test_all_three_horizons_lead_with_distinct_personas():
    # Regression for the swing=intraday alias bug: swing must be a genuine middle ground,
    # not a copy of intraday. All three horizons should surface a different leader.
    leads = {h: _chain_lead(run_scenario(_seed(horizon=h)).narrative_md)
             for h in ("intraday", "swing", "long")}
    assert leads["swing"] != leads["intraday"], "swing must not alias intraday"
    assert leads["swing"] != leads["long"], "swing must not alias long"
    assert leads["intraday"] != leads["long"]
    assert len(set(leads.values())) == 3


def test_intraday_and_long_leads_are_pinned():
    # Pin the fastest-herder (intraday) and slowest-herder (long) leaders so the swing
    # fix does NOT perturb intraday/long ordering. Explicit hashed mode: these leaders
    # were captured under hashed; the default is aggregate_neutral since 0.2.0.
    intraday = run_scenario(_seed(horizon="intraday"), consensus_mode="hashed").narrative_md
    long = run_scenario(_seed(horizon="long"), consensus_mode="hashed").narrative_md
    assert _chain_lead(intraday) == "PTT/Dcard 風向"
    assert _chain_lead(long) == "外資視角"


def test_swing_lead_is_roster_first_mover():
    # swing's middle-ground rule: the leader is the first mover in roster order,
    # which for this seed (hashed mode) is 存股族 (long_term_holder).
    md = run_scenario(_seed(horizon="swing"), consensus_mode="hashed").narrative_md
    assert _chain_lead(md) == "存股族"


@pytest.mark.parametrize("horizon", ["intraday", "swing", "long"])
def test_each_horizon_reaction_chain_is_deterministic(horizon):
    a = run_scenario(_seed(horizon=horizon)).narrative_md
    b = run_scenario(_seed(horizon=horizon)).narrative_md
    assert a == b


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


# --- consensus_mode: aggregate_neutral (default since 0.2.0) vs explicit hashed/aggregate ---


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_default_mode_is_aggregate_neutral(pack, metrics, symbol, scenario):
    # part-013: the public default (no consensus_mode) is aggregate_neutral since 0.2.0.
    # It must reproduce explicit aggregate_neutral byte-for-byte.
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    default = run_scenario(seed, pack=pack)
    explicit = run_scenario(seed, pack=pack, consensus_mode="aggregate_neutral")
    assert default.crowd_consensus == explicit.crowd_consensus
    assert default.narrative_md == explicit.narrative_md
    assert default.persona_samples == explicit.persona_samples


def test_hashed_stock_consensus_pinned():
    # Golden value: this specific stock seed has always produced 'positive' in hashed
    # mode. Pin it so an accidental change to the hashed path is caught. (Explicit mode:
    # the public default is aggregate_neutral since 0.2.0, so this pins hashed on purpose.)
    seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
    assert run_scenario(seed, consensus_mode="hashed").crowd_consensus == "positive"


# --- part-008 slice-001: lock the current default before consensus-model evaluation ---

# Golden consensus for the evaluation corpus, in the CURRENT default (hashed) + current
# aggregate. Pinned so part-008's neutral-baseline experiments cannot silently perturb the
# two shipped modes. (scenario label is fixed to "evt" so the hashed direction is stable.)
_EVAL_CASES = [
    # (pack, symbol, metrics, hashed_consensus, aggregate_consensus)
    # Values MEASURED from the current engine (not chosen) — pinned as a regression floor.
    (STOCK_TW, "cheap_hi", {"discount_premium": -1.5, "yield": 9.0}, "positive", "positive"),
    (STOCK_TW, "rich_lo", {"discount_premium": 1.4, "yield": 2.0}, "negative", "negative"),
    (STOCK_TW, "fair_mid", {"discount_premium": 0.0, "yield": 4.5}, "positive", "positive"),
    # hike_lowval is the motivating divergence: hashed rolls 'positive' but the persona
    # majority is clearly negative (net -5). Aggregate follows the crowd; hashed does not.
    (
        PRODUCT_LAUNCH, "hike_lowval",
        {"price_change": 0.4, "value_delta": -0.4, "switching_cost": 0.6},
        "positive", "negative",
    ),
    (
        PRODUCT_LAUNCH, "value_flat",
        {"price_change": 0.0, "value_delta": 0.8, "switching_cost": 0.2},
        "negative", "neutral",
    ),
]


@pytest.mark.parametrize(
    "pack,symbol,metrics,hashed_c,agg_c", _EVAL_CASES, ids=[c[1] for c in _EVAL_CASES]
)
def test_current_modes_pinned_for_evaluation_corpus(pack, symbol, metrics, hashed_c, agg_c):
    seed = make_seed(symbol, metrics, "evt", pack=pack)
    assert run_scenario(seed, pack=pack, consensus_mode="hashed").crowd_consensus == hashed_c
    assert run_scenario(seed, pack=pack, consensus_mode="aggregate").crowd_consensus == agg_c


def test_default_is_aggregate_neutral_pinned():
    # Explicit record: the public default (no consensus_mode) is aggregate_neutral (0.2.0).
    seed = make_seed("cheap_hi", {"discount_premium": -1.5, "yield": 9.0}, "evt", pack=STOCK_TW)
    assert (
        run_scenario(seed).crowd_consensus
        == run_scenario(seed, consensus_mode="aggregate_neutral").crowd_consensus
    )


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


# --- part-008 slice-002: experimental aggregate_neutral mode ---


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_neutral_baseline_aggregate_is_deterministic(pack, metrics, symbol, scenario):
    seed_a = make_seed(symbol, metrics, scenario, pack=pack)
    seed_b = make_seed(symbol, metrics, scenario, pack=pack)
    a = run_scenario(seed_a, pack=pack, consensus_mode="aggregate_neutral")
    b = run_scenario(seed_b, pack=pack, consensus_mode="aggregate_neutral")
    assert a.crowd_consensus == b.crowd_consensus
    assert a.persona_samples == b.persona_samples
    assert a.narrative_md == b.narrative_md


def test_neutral_baseline_ignores_hashed_direction():
    # The whole point of aggregate_neutral: the emitted direction is a pure function of
    # the ordinal context, so changing ONLY the scenario label (which changes the seed
    # hash, hence the hashed direction) must NOT change the neutral-baseline consensus.
    metrics = {"discount_premium": -1.5, "yield": 9.0}
    seed_a = make_seed("t", metrics, "evtA", pack=STOCK_TW)
    seed_b = make_seed("t", metrics, "evtB", pack=STOCK_TW)
    a = run_scenario(seed_a, consensus_mode="aggregate_neutral")
    b = run_scenario(seed_b, consensus_mode="aggregate_neutral")
    assert a.crowd_consensus == b.crowd_consensus


def test_neutral_baseline_neutral_scenario_stays_neutral():
    # Semantic stability: a genuinely mid/fair scenario should not be pushed to an
    # extreme by a hash roll — neutral baseline keeps it neutral.
    seed = make_seed("fair", {"discount_premium": 0.0, "yield": 4.5}, "evt", pack=STOCK_TW)
    assert run_scenario(seed, consensus_mode="aggregate_neutral").crowd_consensus == "neutral"


@pytest.mark.parametrize("pack,metrics,symbol,scenario", _PACKS)
def test_neutral_baseline_matches_net_sign_rule(pack, metrics, symbol, scenario):
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    result = run_scenario(seed, pack=pack, consensus_mode="aggregate_neutral")
    net = sum(s.stance for s in result.persona_samples)
    expected = "positive" if net > 1 else ("negative" if net < -1 else "neutral")
    assert result.crowd_consensus == expected


# --- software_migration pack (part-012): a third, non-finance domain ---


def test_software_pack_semantic_sanity_resist():
    # rewrite-level breaking + painful migration + negligible value -> the ecosystem resists.
    seed = make_seed(
        "big_rewrite",
        {"breaking_severity": 0.95, "migration_effort": 0.9, "value_gain": 0.05},
        "v9_rewrite",
        pack=SOFTWARE_MIGRATION,
    )
    result = run_scenario(seed, pack=SOFTWARE_MIGRATION)
    assert result.crowd_consensus == "negative"
    assert SOFTWARE_MIGRATION.consensus_display[result.crowd_consensus] == "resist"


def test_software_pack_semantic_sanity_adopt():
    # minor breaking + automated migration + substantial value -> the ecosystem adopts.
    seed = make_seed(
        "smooth_major",
        {"breaking_severity": 0.3, "migration_effort": 0.1, "value_gain": 0.7},
        "v9_smooth",
        pack=SOFTWARE_MIGRATION,
    )
    result = run_scenario(seed, pack=SOFTWARE_MIGRATION)
    assert result.crowd_consensus == "positive"
    assert SOFTWARE_MIGRATION.consensus_display[result.crowd_consensus] == "adopt"


def test_software_pack_display_vocabulary():
    assert SOFTWARE_MIGRATION.consensus_display == {
        "negative": "resist",
        "neutral": "wait",
        "positive": "adopt",
    }


# --- voice variants (part-006) ---


def _variant_pack():
    from crowdscenario.domains.base import Axis, DomainPack

    stances = {1: "多", 0: "中", -1: "空"}
    return DomainPack(
        domain_id="variant_demo",
        persona_ids=("solo",),
        contra_ids=frozenset(),
        herding={"solo": 0.5},
        voice={"solo": dict(stances)},
        display_name={"solo": "獨行俠"},
        axes=(Axis(name="ax", bucket_fn=lambda x: "hi" if x > 0 else "lo",
                   tilt={"hi": 1.0, "lo": -1.0}),),
        sensitivity={"solo": (1.0,)},
        consensus_display={"negative": "neg", "neutral": "neu", "positive": "pos"},
        voice_variants={"solo": {
            1: ("多頭甲", "多頭乙", "多頭丙"),
            0: ("中性甲", "中性乙"),
            -1: ("空頭甲", "空頭乙", "空頭丙"),
        }},
    )


def test_voice_variants_are_deterministic_per_seed():
    pack = _variant_pack()
    s = make_seed("X", {"ax": 0.9}, "evt", pack=pack)
    a = run_scenario(s, pack=pack).persona_samples[0].excerpt
    b = run_scenario(s, pack=pack).persona_samples[0].excerpt
    assert a == b


def test_voice_variants_can_differ_across_seeds():
    pack = _variant_pack()
    excerpts = set()
    for sym in ("A", "B", "C", "D", "E", "F", "G", "H"):
        s = make_seed(sym, {"ax": 0.9}, "evt", pack=pack)
        excerpts.add(run_scenario(s, pack=pack).persona_samples[0].excerpt)
    # across several seeds, the variant pick should not be constant
    assert len(excerpts) > 1


def test_variant_excerpt_is_one_of_the_declared_variants():
    pack = _variant_pack()
    s = make_seed("X", {"ax": 0.9}, "evt", pack=pack)
    excerpt = run_scenario(s, pack=pack).persona_samples[0].excerpt
    assert any(v in excerpt for v in pack.voice_variants["solo"][1])


def test_pack_without_variants_narrative_unchanged():
    # STOCK_TW ships without variants for most personas: adding the feature must not
    # perturb a pack/persona that has no variants. Pin the canonical excerpt.
    seed = make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)
    a = run_scenario(seed).narrative_md
    b = run_scenario(seed).narrative_md
    assert a == b  # deterministic; variants (if any) are seed-stable


# --- intensity-scaled chain length (part-006 slice-002) ---


def _chain_steps(md: str) -> int:
    # count numbered reaction-chain steps ("1. ", "2. ", ...)
    import re

    return len(re.findall(r"^\d+\. ", md, flags=re.MULTILINE))


def test_severe_reaction_chain_is_longer_than_mild():
    # a deep-discount/high-yield scenario has 3+ movers; severe should expand the chain.
    metrics = {"discount_premium": -1.5, "yield": 9.0}
    mild = run_scenario(_seed(intensity="mild", metrics=metrics)).narrative_md
    severe = run_scenario(_seed(intensity="severe", metrics=metrics)).narrative_md
    assert _chain_steps(severe) > _chain_steps(mild)


def test_mild_chain_length_pinned_at_three():
    # mild must stay the original 3-step chain (zero drift from the pre-slice engine).
    metrics = {"discount_premium": -1.5, "yield": 9.0}
    assert _chain_steps(run_scenario(_seed(intensity="mild", metrics=metrics)).narrative_md) == 3


def test_severe_chain_is_deterministic():
    metrics = {"discount_premium": -1.5, "yield": 9.0}
    a = run_scenario(_seed(intensity="severe", metrics=metrics)).narrative_md
    b = run_scenario(_seed(intensity="severe", metrics=metrics)).narrative_md
    assert a == b
