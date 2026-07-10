"""Shared case-study runner (part-010).

Given a case spec (a pack, a symbol, raw metrics, a scenario label, and your OWN
posture), this reproduces everything a case study reports: the buckets the raw metrics
collapse to, the crowd consensus under all three modes, the persona stance distribution,
a horizon × intensity sweep, and the crowd-vs-your-own divergence with its storylines.

It is deterministic and offline — running it twice yields identical results. The raw
metric numbers appear ONLY in the ``raw_metrics`` field (the input); they never reach the
buckets, personas, or narrative (self-demonstrating the firewall).

These case studies are scenario REHEARSALS, not forecasts or backtests. They show how the
engine reasons and where it must not be trusted — not what a real market/user will do.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crowdscenario import (
    DomainPack,
    compose_divergence,
    make_seed,
    run_scenario,
)

_MODES = ("aggregate_neutral", "hashed", "aggregate")  # default first
_HORIZONS = ("intraday", "swing", "long")
_INTENSITIES = ("mild", "severe")


@dataclass(frozen=True)
class CaseSpec:
    label: str
    pack: DomainPack
    symbol: str
    scenario: str
    raw_metrics: dict[str, float]
    your_posture: str  # your own read, for the divergence panel


@dataclass(frozen=True)
class CaseResult:
    label: str
    domain: str
    buckets: dict[str, str]
    consensus_by_mode: dict[str, str]
    stance_distribution: dict[int, int]  # stance -> count (default mode)
    persona_lines: tuple[tuple[str, int, str], ...]  # (display_name, stance, voice)
    sweep: tuple[tuple[str, str, str], ...]  # (horizon, intensity, consensus)
    your_posture: str
    divergence_bucket: str
    divergence_storylines: tuple[str, ...]
    narrative_md: str  # default-mode narrative
    raw_metrics: dict[str, float] = field(default_factory=dict)


def run_case(spec: CaseSpec) -> CaseResult:
    pack = spec.pack
    seed = make_seed(spec.symbol, spec.raw_metrics, spec.scenario, pack=pack)

    consensus_by_mode = {
        mode: run_scenario(seed, pack=pack, consensus_mode=mode).crowd_consensus
        for mode in _MODES
    }

    default = run_scenario(seed, pack=pack)  # aggregate_neutral (0.2.0 default)
    dist: dict[int, int] = {-1: 0, 0: 0, 1: 0}
    persona_lines: list[tuple[str, int, str]] = []
    for s in default.persona_samples:
        dist[s.stance] += 1
        name = pack.display_name.get(s.archetype_id, s.archetype_id)
        voice = pack.voice[s.archetype_id][s.stance]
        persona_lines.append((name, s.stance, voice))

    sweep: list[tuple[str, str, str]] = []
    for h in _HORIZONS:
        for i in _INTENSITIES:
            s = make_seed(spec.symbol, spec.raw_metrics, spec.scenario,
                          horizon=h, intensity=i, pack=pack)
            sweep.append((h, i, run_scenario(s, pack=pack).crowd_consensus))

    div = compose_divergence(default, spec.your_posture)

    return CaseResult(
        label=spec.label,
        domain=pack.domain_id,
        buckets=dict(seed.ordinal_context),
        consensus_by_mode=consensus_by_mode,
        stance_distribution=dist,
        persona_lines=tuple(persona_lines),
        sweep=tuple(sweep),
        your_posture=spec.your_posture,
        divergence_bucket=div.divergence_bucket,
        divergence_storylines=div.storylines,
        narrative_md=default.narrative_md,
        raw_metrics=dict(spec.raw_metrics),
    )
