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
