"""Compute crowd-vs-external divergence at report time (no write-back).

The engine never knows your own posture — it is firewalled from it. So the
divergence between the synthetic crowd and your own read is computed *here*, at
report time, from the crowd narrative plus a posture you supply. It emits a
categorical bucket + intensity, never a scalar that could tilt a decision.
"""

from __future__ import annotations

from crowdscenario.contracts import CrowdNarrative, NarrativeDivergence

_ORDER = {"negative": -1, "neutral": 0, "positive": 1}
_BUCKETS = ("LOW", "MEDIUM", "HIGH")


def posture_from_score(score: float) -> str:
    """Turn any numeric read in roughly [-1, +1] into a categorical posture.

    Convenience so callers with their own composite/score can get a posture to
    diff against the crowd. The number stops here — only the label goes forward.
    Returns the domain-neutral vocabulary (negative | neutral | positive).
    """
    if score > 0.1:
        return "positive"
    if score < -0.1:
        return "negative"
    return "neutral"


def compose_divergence(narrative: CrowdNarrative, external_posture: str) -> NarrativeDivergence:
    """Diff the synthetic crowd stance against your own categorical posture."""
    gap = abs(_ORDER[narrative.crowd_consensus] - _ORDER[external_posture])  # 0 | 1 | 2
    return NarrativeDivergence(
        seed_id=narrative.seed_id,
        crowd_consensus=narrative.crowd_consensus,
        external_posture=external_posture,
        divergence_bucket=_BUCKETS[gap],
        narrative_intensity=gap + 1,
    )
