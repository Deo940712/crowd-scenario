"""Composer: crowd-vs-your-own divergence + counterfactual storylines (part-004).

The divergence artifact is report-time only and carries no scalar. These lock the
storyline behaviour: it reacts to the divergence bucket, is deterministic, stays
conditional (rehearsal, not advice), and never carries a numeric market token.
"""

from __future__ import annotations

import pytest

from crowdscenario import (
    CrowdNarrative,
    compose_divergence,
    posture_from_score,
    scan_violations,
)
from crowdscenario.contracts import ContractError


def _narrative(consensus: str) -> CrowdNarrative:
    return CrowdNarrative(
        seed_id="seed_x", rng_seed=42, n_personas=30, crowd_consensus=consensus, narrative_md="x"
    )


def test_high_divergence_has_storylines():
    # crowd positive vs your negative -> gap 2 -> HIGH -> counterfactual storylines
    div = compose_divergence(_narrative("positive"), "negative")
    assert div.divergence_bucket == "HIGH"
    assert div.storylines  # non-empty


def test_low_divergence_storyline_signals_agreement():
    div = compose_divergence(_narrative("neutral"), "neutral")
    assert div.divergence_bucket == "LOW"
    assert div.storylines
    assert any("一致" in s for s in div.storylines)


def test_storylines_are_deterministic():
    a = compose_divergence(_narrative("positive"), "negative").storylines
    b = compose_divergence(_narrative("positive"), "negative").storylines
    assert a == b


def test_storylines_carry_no_numeric_market_token():
    for consensus in ("negative", "neutral", "positive"):
        for external in ("negative", "neutral", "positive"):
            div = compose_divergence(_narrative(consensus), external)
            for line in div.storylines:
                assert scan_violations(line) == (), f"leak in {line!r}"


def test_storylines_reachable_via_posture_from_score():
    # end-to-end convenience path: your own score -> posture -> divergence storylines
    div = compose_divergence(_narrative("negative"), posture_from_score(0.9))
    assert div.divergence_bucket == "HIGH"
    assert div.storylines


def test_compose_divergence_rejects_out_of_vocabulary_posture():
    # An out-of-vocabulary posture must be a clean ContractError, not a raw KeyError
    # leaking from the internal _ORDER lookup.
    with pytest.raises(ContractError):
        compose_divergence(_narrative("neutral"), "sideways")
