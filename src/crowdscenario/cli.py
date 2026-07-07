"""Command-line entry point: run one crowd rehearsal, or check determinism.

    python -m crowdscenario run --symbol 0056 --scenario 0056_cut
    python -m crowdscenario run --symbol 0056 --scenario 升息 --horizon long --intensity severe
    python -m crowdscenario run --domain product_launch --symbol newfeature --scenario price_hike
    python -m crowdscenario run --symbol 0056 --scenario 0056_cut --consensus-mode aggregate
    python -m crowdscenario run --symbol MYETF --scenario evt --metrics '{"yield": 8.5, ...}'
    python -m crowdscenario verify --symbol 0056 --scenario 0056_cut

The engine is deterministic and reads no network — safe to run anywhere. ``--domain``
selects which pluggable persona/axis pack to rehearse (defaults to ``stock_tw`` so the
original commands behave identically). ``--consensus-mode`` picks how the crowd
direction is decided: ``hashed`` (seed-derived, the default) or ``aggregate`` (the
persona majority, so the direction follows the scenario). ``--metrics`` feeds your own
raw metrics as a JSON object (overriding the built-in demo fixtures); only their ordinal
buckets survive into the seed, so no raw number ever crosses the firewall.
"""

from __future__ import annotations

import argparse
import json
import sys

from crowdscenario.contracts import ContractError
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


def _metrics_for(
    domain: str, symbol: str, override: dict[str, float] | None = None
) -> dict[str, float]:
    """Resolve the raw metrics for a run: explicit override > fixture > neutral fallback.

    An ``override`` (from ``--metrics``) always wins. Otherwise a built-in demo fixture
    is used. If neither exists, a neutral per-axis fallback is returned AND a warning is
    printed to stderr — the CLI must never *silently* substitute made-up neutral data
    (the library API already fails fast; only the demo CLI keeps a fallback, loudly).
    """
    if override is not None:
        return override
    fixture = _FIXTURES.get(domain, {}).get(symbol)
    if fixture is not None:
        return fixture
    print(
        f"warning: no fixture or --metrics for {symbol!r} in domain {domain!r}; "
        "using neutral fallback (demo only)",
        file=sys.stderr,
    )
    return _FALLBACK[domain]


def _parse_metrics(raw: str | None) -> dict[str, float] | None:
    """Parse the --metrics JSON string into a metrics dict, or None if not given.

    Raises ValueError with a clean message on malformed JSON or a non-object payload,
    so the caller can report it without a traceback.
    """
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--metrics is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("--metrics must be a JSON object, e.g. '{\"yield\": 8.5}'")
    return parsed


_SWEEP_HORIZONS = ("intraday", "swing", "long")
_SWEEP_INTENSITIES = ("mild", "severe")


def _build_run_dict(
    args: argparse.Namespace,
    pack: DomainPack,
    override: dict[str, float] | None,
    horizon: str,
    intensity: str,
) -> dict[str, object]:
    """Run one rehearsal and shape it into the CLI's JSON dict (may raise ContractError)."""
    seed = make_seed(
        args.symbol,
        _metrics_for(args.domain, args.symbol, override),
        market_scenario_label=args.scenario,
        rng_seed=args.seed,
        horizon=horizon,
        intensity=intensity,
        pack=pack,
    )
    n = run_scenario(seed, pack=pack, n_personas=args.n, consensus_mode=args.consensus_mode)
    return {
        "domain": pack.domain_id,
        "seed_id": n.seed_id,
        "artifact_type": n.artifact_type,
        "schema_version": n.schema_version,
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


def cmd_run(args: argparse.Namespace) -> int:
    pack = _DOMAINS[args.domain]
    try:
        override = _parse_metrics(args.metrics)
        if args.sweep:
            # One rehearsal per horizon × intensity cell — a comparison grid.
            rows = [
                _build_run_dict(args, pack, override, h, i)
                for h in _SWEEP_HORIZONS
                for i in _SWEEP_INTENSITIES
            ]
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            out = _build_run_dict(args, pack, override, args.horizon, args.intensity)
            print(json.dumps(out, ensure_ascii=False, indent=2))
    except (ValueError, ContractError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
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
    p_run.add_argument(
        "--metrics",
        default=None,
        help="raw metrics as a JSON object, e.g. '{\"discount_premium\": -0.6, "
        '"yield": 8.5}\'. Overrides the built-in fixture; only the ordinal buckets '
        "survive into the seed (raw numbers never leave make_seed).",
    )
    p_run.add_argument(
        "--sweep",
        action="store_true",
        help="rehearse every horizon × intensity cell (3×2) and emit a JSON array grid "
        "instead of a single object (ignores --horizon/--intensity).",
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
