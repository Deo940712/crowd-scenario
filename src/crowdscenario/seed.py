"""Build a frozen, bucketed ScenarioSeed from raw metrics.

Raw numbers are dropped here — only ordinal buckets cross the firewall, so the
crowd personas can never see or echo an authoritative figure. This is the ONLY
place a raw number is turned into the seed the engine reads.

Bucketing is driven by the domain pack's axes: each axis projects one raw metric to
an ordinal bucket via its own ``bucket_fn``. The stock pack keeps the original
``discount_premium`` + ``yield`` axes; another domain supplies its own.
"""

from __future__ import annotations

import hashlib
import json

from crowdscenario.contracts import ContractError, ScenarioSeed
from crowdscenario.domains import DomainPack
from crowdscenario.domains.stock_tw import STOCK_TW


def make_seed(
    symbol: str,
    metrics: dict[str, float],
    market_scenario_label: str,
    rng_seed: int = 42,
    horizon: str = "swing",
    intensity: str = "mild",
    pack: DomainPack = STOCK_TW,
) -> ScenarioSeed:
    """Project raw ``metrics`` into a bucketed, hashed ScenarioSeed.

    Each axis on ``pack`` reads its own raw metric from ``metrics`` and buckets it;
    only the ordinal buckets survive into the seed. A metric the pack's axes require
    but ``metrics`` omits is a fail-fast ``ContractError`` (never a silent ``0.0``),
    so a typo'd axis name in a new domain is caught at the boundary instead of
    producing a plausible-but-wrong seed. ``domain_id``, horizon + intensity all feed
    the hash, so a different domain or rehearsal dimension is a different seed (distinct
    chain), while determinism holds per full seed. All hashed structures go through
    ``json.dumps(sort_keys=True)`` so key order can never perturb the hash.
    """
    missing = [axis.name for axis in pack.axes if axis.name not in metrics]
    if missing:
        raise ContractError(f"missing metric(s) for axis/axes: {', '.join(sorted(missing))}")
    ordinal = {axis.name: axis.bucket_fn(metrics[axis.name]) for axis in pack.axes}
    seed_hash = hashlib.sha256(
        json.dumps(
            {
                "domain": pack.domain_id,
                "symbol": symbol,
                "label": market_scenario_label,
                "rng": rng_seed,
                "ordinal": ordinal,
                "horizon": horizon,
                "intensity": intensity,
            },
            sort_keys=True,
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()[:16]
    return ScenarioSeed(
        seed_id=f"seed_{symbol}_{seed_hash[:8]}",
        rng_seed=rng_seed,
        market_scenario_label=market_scenario_label,
        domain_id=pack.domain_id,
        ordinal_context=ordinal,
        seed_hash=seed_hash,
        horizon=horizon,
        intensity=intensity,
    )
