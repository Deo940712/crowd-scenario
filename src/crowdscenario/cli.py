"""Command-line entry point: run one crowd rehearsal, or check determinism.

    python -m crowdscenario run --symbol 0056 --scenario 0056_cut
    python -m crowdscenario run --symbol 0056 --scenario 升息 --horizon long --intensity severe
    python -m crowdscenario run --domain product_launch --symbol newfeature --scenario price_hike
    python -m crowdscenario run --symbol 0056 --scenario 0056_cut --consensus-mode aggregate
    python -m crowdscenario verify --symbol 0056 --scenario 0056_cut

The engine is deterministic and reads no network — safe to run anywhere. ``--domain``
selects which pluggable persona/axis pack to rehearse (defaults to ``stock_tw`` so the
original commands behave identically). ``--consensus-mode`` picks how the crowd
direction is decided: ``hashed`` (seed-derived, the default) or ``aggregate`` (the
persona majority, so the direction follows the scenario).
"""

from __future__ import annotations

import argparse
import json
import sys

from crowdscenario.domains import DomainPack
from crowdscenario.domains.product import PRODUCT_LAUNCH
from crowdscenario.domains.stock_tw import STOCK_TW
from crowdscenario.engine import run_scenario
from crowdscenario.seed import make_seed

# Domain packs resolvable by name from the CLI. The API injects a pack object directly;
# this string lookup is a CLI convenience only.
_DOMAINS: dict[str, DomainPack] = {
    "stock_tw": STOCK_TW,
    "product_launch": PRODUCT_LAUNCH,
}

# Tiny built-in fixtures per domain so the CLI runs with zero setup. These are
# illustrative ordinal inputs, NOT live data — the engine only ever sees the buckets.
_FIXTURES: dict[str, dict[str, dict[str, float]]] = {
    "stock_tw": {
        "0050": {"discount_premium": -0.05, "yield": 4.2},
        "0056": {"discount_premium": -0.6, "yield": 8.5},
        "00878": {"discount_premium": 1.4, "yield": 3.1},
        "00919": {"discount_premium": -0.41, "yield": 9.2},
    },
    "product_launch": {
        "price_hike": {"price_change": 0.3, "value_delta": -0.2, "switching_cost": 0.3},
        "big_feature": {"price_change": 0.0, "value_delta": 0.7, "switching_cost": 0.5},
        "redesign": {"price_change": 0.0, "value_delta": -0.4, "switching_cost": 0.6},
    },
}

# Per-domain fallback when a symbol has no fixture: a neutral mid-point for each axis.
_FALLBACK: dict[str, dict[str, float]] = {
    "stock_tw": {"discount_premium": 0.0, "yield": 4.0},
    "product_launch": {"price_change": 0.0, "value_delta": 0.0, "switching_cost": 0.5},
}


def _metrics_for(domain: str, symbol: str) -> dict[str, float]:
    return _FIXTURES.get(domain, {}).get(symbol, _FALLBACK[domain])


def cmd_run(args: argparse.Namespace) -> int:
    pack = _DOMAINS[args.domain]
    seed = make_seed(
        args.symbol,
        _metrics_for(args.domain, args.symbol),
        market_scenario_label=args.scenario,
        rng_seed=args.seed,
        horizon=args.horizon,
        intensity=args.intensity,
        pack=pack,
    )
    n = run_scenario(seed, pack=pack, n_personas=args.n, consensus_mode=args.consensus_mode)
    out = {
        "domain": pack.domain_id,
        "seed_id": n.seed_id,
        "artifact_type": n.artifact_type,
        "crowd_consensus": n.crowd_consensus,
        "consensus_display": pack.consensus_display.get(n.crowd_consensus, n.crowd_consensus),
        "consensus_mode": args.consensus_mode,
        "non_authoritative": n.non_authoritative,
        "synthetic_population": n.synthetic_population,
        "n_personas": n.n_personas,
        "horizon": seed.horizon,
        "intensity": seed.intensity,
        "narrator_backend": n.narrator_backend,
        "narrator_notes": list(n.narrator_notes),
        "narrative_md": n.narrative_md,
        "persona_samples": [
            {"archetype_id": s.archetype_id, "stance": s.stance, "excerpt": s.excerpt}
            for s in n.persona_samples
        ],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    pack = _DOMAINS[args.domain]

    def once() -> tuple[str, str, str, tuple]:
        # Compare the FULL deterministic artifact, not just the consensus: narrative,
        # persona samples and seed_id must all be byte-stable, or determinism is a lie
        # even when the top-level stance happens to match. horizon/intensity feed the
        # seed hash, so they are exercised here too.
        seed = make_seed(
            args.symbol,
            _metrics_for(args.domain, args.symbol),
            market_scenario_label=args.scenario,
            rng_seed=args.seed,
            horizon=args.horizon,
            intensity=args.intensity,
            pack=pack,
        )
        n = run_scenario(seed, pack=pack)
        return (n.seed_id, n.crowd_consensus, n.narrative_md, n.persona_samples)

    a, b = once(), once()
    ok = a == b
    print(
        f"determinism [{pack.domain_id}/{args.symbol} "
        f"horizon={args.horizon} intensity={args.intensity}]: "
        f"consensus={a[1]!r} full_artifact_stable={a == b} -> {'OK' if ok else 'FAIL'}"
    )
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crowdscenario", description="Deterministic crowd rehearsal.")
    sub = p.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run one crowd rehearsal (JSON)")
    p_run.add_argument("--domain", choices=sorted(_DOMAINS), default="stock_tw")
    p_run.add_argument("--symbol", default="0056")
    p_run.add_argument("--scenario", default="0056_cut")
    p_run.add_argument("--seed", type=int, default=42)
    p_run.add_argument("--n", type=int, default=30)
    p_run.add_argument("--horizon", choices=["intraday", "swing", "long"], default="swing")
    p_run.add_argument("--intensity", choices=["mild", "severe"], default="mild")
    p_run.add_argument(
        "--consensus-mode",
        choices=["hashed", "aggregate"],
        default="hashed",
        help="how the crowd direction is decided: hashed (seed-derived, default) or "
        "aggregate (persona majority)",
    )
    p_run.set_defaults(func=cmd_run)

    p_verify = sub.add_parser("verify", help="offline determinism check (full artifact)")
    p_verify.add_argument("--domain", choices=sorted(_DOMAINS), default="stock_tw")
    p_verify.add_argument("--symbol", default="0056")
    p_verify.add_argument("--scenario", default="0056_cut")
    p_verify.add_argument("--seed", type=int, default=42)
    p_verify.add_argument("--horizon", choices=["intraday", "swing", "long"], default="swing")
    p_verify.add_argument("--intensity", choices=["mild", "severe"], default="mild")
    p_verify.set_defaults(func=cmd_verify)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
