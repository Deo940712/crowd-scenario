"""Contract invariants ??the crowd artifacts are non-authoritative and scalar-free.

These are the firewall's teeth in code: the crowd narrative and the divergence
carry no numeric modifier, reject out-of-vocabulary values, and are hard-wired
non-authoritative.
"""

from __future__ import annotations

import dataclasses

import pytest

from crowdscenario.contracts import (
    ContractError,
    CrowdNarrative,
    NarrativeDivergence,
    PersonaReaction,
    ScenarioSeed,
)
from crowdscenario.domains.base import Axis, DomainPack


def _cn(**overrides):
    base = dict(
        seed_id="seed_x", rng_seed=42, n_personas=30, crowd_consensus="negative", narrative_md="x"
    )
    base.update(overrides)
    return CrowdNarrative(**base)


def test_crowd_narrative_is_non_authoritative_by_default():
    assert _cn().non_authoritative is True
    assert _cn().synthetic_population is True


def test_crowd_narrative_rejects_non_synthetic_population():
    with pytest.raises(ContractError):
        _cn(synthetic_population=False)


def test_crowd_narrative_rejects_bad_consensus():
    with pytest.raises(ContractError):
        _cn(crowd_consensus="up")


def test_crowd_narrative_rejects_bad_persona_count():
    with pytest.raises(ContractError):
        _cn(n_personas=5)


def test_crowd_narrative_has_no_numeric_modifier_field():
    names = {f.name for f in dataclasses.fields(CrowdNarrative)}
    assert "contrarian_modifier" not in names
    assert "modifier" not in names


def test_crowd_narrative_has_string_schema_version():
    n = _cn()
    assert n.schema_version == "1"
    assert isinstance(n.schema_version, str)  # a label, never a numeric scalar


def _nd(**overrides):
    base = dict(
        seed_id="seed_x",
        crowd_consensus="negative",
        external_posture="neutral",
        divergence_bucket="MEDIUM",
        narrative_intensity=2,
    )
    base.update(overrides)
    return NarrativeDivergence(**base)


def test_divergence_is_non_authoritative_by_default():
    assert _nd().non_authoritative is True


def test_divergence_rejects_non_synthetic_population():
    with pytest.raises(ContractError):
        _nd(synthetic_population=False)


def test_divergence_rejects_bad_bucket():
    with pytest.raises(ContractError):
        _nd(divergence_bucket="EXTREME")


def test_divergence_rejects_bad_intensity():
    with pytest.raises(ContractError):
        _nd(narrative_intensity=5)


def test_divergence_has_no_numeric_modifier_field():
    names = {f.name for f in dataclasses.fields(NarrativeDivergence)}
    assert "contrarian_modifier" not in names
    assert "modifier" not in names


def test_scenario_seed_rejects_bad_horizon_intensity():
    with pytest.raises(ContractError):
        ScenarioSeed("s", 42, "L", horizon="weekly")
    with pytest.raises(ContractError):
        ScenarioSeed("s", 42, "L", intensity="nuclear")


# --- ScenarioSeed.ordinal_context: only ordinal STRINGS may cross the firewall ---
#
# The read-side contract exists so a raw price/yield can never ride into the engine.
# make_seed produces str->str buckets, but a direct constructor call must not be able
# to smuggle a number (or an empty label) past the door.


@pytest.mark.parametrize(
    "bad_context",
    [
        {"raw_price": 123.45},   # float value = raw number leak
        {"count": 7},            # int value
        {"flag": True},          # bool value (a bool is an int subclass)
        {"discount": ""},        # empty-string value is not a real bucket
        {"nested": {"a": "b"}},  # dict value
        {"listy": ["a"]},        # list value
        {5: "deep_discount"},    # non-string key
        {"": "deep_discount"},   # empty-string key
    ],
)
def test_scenario_seed_rejects_non_string_ordinal_context(bad_context):
    with pytest.raises(ContractError):
        ScenarioSeed("s", 42, "L", ordinal_context=bad_context)


def test_scenario_seed_accepts_valid_ordinal_context():
    seed = ScenarioSeed("s", 42, "L", ordinal_context={"discount_premium": "deep_discount"})
    assert seed.ordinal_context["discount_premium"] == "deep_discount"


# --- PersonaReaction: a stance is a bounded categorical label, never a free integer ---


def test_persona_reaction_accepts_valid():
    r = PersonaReaction("archetype_a", -1, "zh-TW", "some excerpt")
    assert r.stance == -1
    assert r.is_synthetic is True


@pytest.mark.parametrize("bad_stance", [2, 999, -2, True, False])
def test_persona_reaction_rejects_out_of_range_stance(bad_stance):
    # True/False must be rejected too: bool is an int subclass, and True == 1 would
    # otherwise sneak past a bare ``in (-1, 0, 1)`` check.
    with pytest.raises(ContractError):
        PersonaReaction("a", bad_stance, "zh-TW", "x")


def test_persona_reaction_rejects_non_synthetic():
    with pytest.raises(ContractError):
        PersonaReaction("a", 0, "zh-TW", "x", is_synthetic=False)


@pytest.mark.parametrize("kwargs", [{"archetype_id": ""}, {"register": ""}])
def test_persona_reaction_rejects_empty_string_fields(kwargs):
    base = dict(archetype_id="a", stance=0, register="zh-TW", excerpt="x")
    base.update(kwargs)
    with pytest.raises(ContractError):
        PersonaReaction(**base)


def test_persona_reaction_rejects_non_string_excerpt():
    with pytest.raises(ContractError):
        PersonaReaction("a", 0, "zh-TW", 5)


# --- DomainPack invariants: the firewall's teeth for the pluggable layer ---
#
# validate_pack runs in __post_init__, so an invalid pack cannot even be constructed.
# These lock the four load-bearing invariants for ANY pack, not just the stock one.


def _pack(**overrides):
    base = dict(
        domain_id="t",
        persona_ids=("a", "b"),
        contra_ids=frozenset({"a"}),
        herding={"a": 0.2, "b": 0.8},
        voice={"a": {1: "x", 0: "y", -1: "z"}, "b": {1: "x", 0: "y", -1: "z"}},
        display_name={"a": "A", "b": "B"},
        axes=(Axis(name="ax", bucket_fn=lambda x: "mid", tilt={"mid": 0.0}),),
        sensitivity={"a": (0.5,), "b": (0.5,)},
        consensus_display={"negative": "neg", "neutral": "neu", "positive": "pos"},
    )
    base.update(overrides)
    return DomainPack(**base)


def test_valid_pack_constructs():
    assert _pack().domain_id == "t"


def test_pack_rejects_empty_personas():
    with pytest.raises(ContractError):
        _pack(persona_ids=(), sensitivity={}, herding={}, voice={}, display_name={})


def test_pack_rejects_duplicate_personas():
    with pytest.raises(ContractError):
        _pack(persona_ids=("a", "a"))


def test_pack_rejects_misaligned_parallel_table():
    # herding is missing persona "b" -> keys != persona_ids
    with pytest.raises(ContractError):
        _pack(herding={"a": 0.2})


def test_pack_rejects_extra_key_in_parallel_table():
    with pytest.raises(ContractError):
        _pack(display_name={"a": "A", "b": "B", "c": "C"})


def test_pack_rejects_sensitivity_length_mismatch():
    # one axis but a two-weight sensitivity tuple
    with pytest.raises(ContractError):
        _pack(sensitivity={"a": (0.5, 0.5), "b": (0.5,)})


def test_pack_rejects_contra_not_subset():
    with pytest.raises(ContractError):
        _pack(contra_ids=frozenset({"a", "ghost"}))


def test_pack_rejects_incomplete_consensus_display():
    with pytest.raises(ContractError):
        _pack(consensus_display={"negative": "neg", "neutral": "neu"})


def test_pack_rejects_non_string_consensus_display():
    # a numeric display value would be a firewall leak
    with pytest.raises(ContractError):
        _pack(consensus_display={"negative": 0, "neutral": "neu", "positive": "pos"})


# --- optional voice_variants (part-006) ---


def test_pack_accepts_valid_voice_variants():
    p = _pack(voice_variants={"a": {1: ("x1", "x2"), 0: ("y1",), -1: ("z1", "z2")}})
    assert p.voice_variants["a"][1] == ("x1", "x2")


def test_pack_without_variants_defaults_empty():
    assert _pack().voice_variants == {}


def test_pack_rejects_variants_for_unknown_persona():
    with pytest.raises(ContractError):
        _pack(voice_variants={"ghost": {1: ("x",)}})


def test_pack_rejects_empty_variant_tuple():
    with pytest.raises(ContractError):
        _pack(voice_variants={"a": {1: ()}})


def test_pack_rejects_non_string_variant():
    with pytest.raises(ContractError):
        _pack(voice_variants={"a": {1: ("ok", 5)}})


# --- finite-numeric invariants: NaN/inf/bool are not valid ordering/threshold inputs ---
#
# tilt/herding/sensitivity are internal floats. A NaN would silently corrupt sorting and
# stance math (NaN compares false to everything); a bool is not a real weight. Reject both.

_BAD_NUMS = [float("nan"), float("inf"), float("-inf"), True]


@pytest.mark.parametrize("bad", _BAD_NUMS)
def test_pack_rejects_non_finite_tilt(bad):
    with pytest.raises(ContractError):
        _pack(axes=(Axis(name="ax", bucket_fn=lambda x: "mid", tilt={"mid": bad}),))


@pytest.mark.parametrize("bad", _BAD_NUMS)
def test_pack_rejects_non_finite_herding(bad):
    with pytest.raises(ContractError):
        _pack(herding={"a": bad, "b": 0.8})


@pytest.mark.parametrize("bad", _BAD_NUMS)
def test_pack_rejects_non_finite_sensitivity(bad):
    with pytest.raises(ContractError):
        _pack(sensitivity={"a": (bad,), "b": (0.5,)})


# --- voice_variants stance keys are bounded categorical labels, not free integers ---


@pytest.mark.parametrize("bad_stance", [999, 2, -2, True])
def test_pack_rejects_out_of_range_variant_stance(bad_stance):
    with pytest.raises(ContractError):
        _pack(voice_variants={"a": {bad_stance: ("x",)}})


# --- deep immutability: a validated pack cannot be mutated back into an invalid state ---
#
# frozen=True only blocks rebinding attributes, not mutating the dicts they point at.
# After validation the pack's mappings are read-only, so a lookup can never be corrupted
# post-construction. Mutation raises TypeError (standard read-only mapping behaviour).


def test_pack_reads_still_work_after_freeze():
    p = _pack()
    assert p.herding["a"] == 0.2
    assert p.voice["a"][1] == "x"
    assert p.axes[0].tilt["mid"] == 0.0


def test_pack_herding_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.herding["a"] = 9


def test_pack_voice_is_deep_read_only():
    p = _pack()
    # Item assignment is the canonical read-only proof (raises TypeError). A read-only
    # mapping also has no ``clear`` at all (AttributeError), so mutation is impossible
    # either way.
    with pytest.raises(TypeError):
        p.voice["a"][1] = "hack"
    with pytest.raises(AttributeError):
        p.voice["a"].clear()


def test_pack_display_name_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.display_name["a"] = "X"


def test_pack_sensitivity_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.sensitivity["a"] = (9,)


def test_pack_consensus_display_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.consensus_display["negative"] = "n2"


def test_pack_horizon_frame_is_read_only():
    p = _pack(horizon_frame={"swing": "frame"})
    with pytest.raises(TypeError):
        p.horizon_frame["swing"] = "x"


def test_pack_axis_tilt_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.axes[0].tilt["mid"] = 9


def test_pack_voice_variants_is_deep_read_only():
    p = _pack(voice_variants={"a": {1: ("x1", "x2")}})
    with pytest.raises(TypeError):
        p.voice_variants["a"][1] = ("hack",)


# --- pack-overridable register + intensity_display (part-015) -----------------------
#
# The persona register and the intensity display words used to be hardcoded in the
# engine ("zh-TW", 溫和/劇烈). They now live on the pack so a non-Chinese domain can
# speak its own language; the defaults reproduce the exact old values, keeping the
# three shipped packs byte-identical.


def test_pack_register_defaults_to_zh_tw():
    assert _pack().register == "zh-TW"


def test_pack_intensity_display_defaults_to_old_words():
    p = _pack()
    assert p.intensity_display["mild"] == "溫和"
    assert p.intensity_display["severe"] == "劇烈"


def test_pack_register_and_intensity_display_are_overridable():
    p = _pack(register="en", intensity_display={"mild": "mild", "severe": "strong"})
    assert p.register == "en"
    assert p.intensity_display["severe"] == "strong"


def test_pack_rejects_non_string_register():
    with pytest.raises(ContractError):
        _pack(register=5)


def test_pack_rejects_empty_register():
    with pytest.raises(ContractError):
        _pack(register="")


def test_pack_rejects_non_string_intensity_display_value():
    with pytest.raises(ContractError):
        _pack(intensity_display={"mild": 1, "severe": "strong"})


def test_pack_rejects_incomplete_intensity_display():
    # must cover the full INTENSITIES vocabulary (mild + severe)
    with pytest.raises(ContractError):
        _pack(intensity_display={"mild": "gentle"})


def test_pack_intensity_display_is_read_only():
    p = _pack()
    with pytest.raises(TypeError):
        p.intensity_display["mild"] = "x"
