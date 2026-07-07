"""Worked example: feed your OWN real metrics into the firewalled engine — safely.

The point of the firewall is that the crowd layer can read real, decision-grade numbers
(a sentiment score you scraped, a yield, a discount) WITHOUT any of them leaking back
out: ``make_seed`` buckets each raw metric into an ordinal label and drops the number,
so the personas only ever see e.g. ``"deep_discount"``, never ``-1.5``.

This file shows the injection pattern: you supply a ``fetch_metrics(symbol) -> dict``
(your crawler / data layer), and the engine does the rest. Here ``fetch_metrics`` is a
fake, offline, deterministic stand-in so the example is runnable and testable with zero
dependencies — swap it for your real source and nothing else changes.

Run it:

    # (needs the package importable; from the repo root:)
    #   PowerShell:  $env:PYTHONPATH='src'; python examples/real_data.py
    #   bash:        PYTHONPATH=src python examples/real_data.py

Rehearsal, not a forecast: this decides no number and writes back into no decision.
"""

from __future__ import annotations

from crowdscenario import STOCK_TW, make_seed, run_scenario


def fetch_metrics(symbol: str) -> dict[str, float]:
    """Stand-in for YOUR data layer: return raw metrics for a symbol.

    In real use this is where a crawler / API / DB read would go (e.g. a PTT sentiment
    score, a live discount-to-NAV, a trailing yield). It is offline and deterministic
    here on purpose; the engine never sees these raw numbers — only their buckets do.
    """
    table = {
        "0056": {"discount_premium": -0.6, "yield": 8.5},
        "0050": {"discount_premium": -0.05, "yield": 4.2},
    }
    # A symbol you have no data for still needs every axis; supply a neutral default.
    return table.get(symbol, {"discount_premium": 0.0, "yield": 4.0})


def rehearse(symbol: str, scenario: str) -> dict[str, object]:
    """Fetch raw metrics, bucket them behind the firewall, and rehearse the crowd.

    Returns only categorical, firewall-safe facts — the same thing the CLI would emit.
    """
    raw = fetch_metrics(symbol)  # real numbers live ONLY in this local variable...
    seed = make_seed(symbol, raw, market_scenario_label=scenario, pack=STOCK_TW)
    # ...and are gone by here: seed carries buckets, not numbers.
    narrative = run_scenario(seed, pack=STOCK_TW, consensus_mode="aggregate")
    return {
        "symbol": symbol,
        "crowd_consensus": narrative.crowd_consensus,
        "consensus_display": STOCK_TW.consensus_display[narrative.crowd_consensus],
        "ordinal_context": dict(seed.ordinal_context),  # buckets that crossed the firewall
        "narrative_md": narrative.narrative_md,
    }


def main() -> None:
    for symbol in ("0056", "0050"):
        result = rehearse(symbol, scenario="rate_cut")
        print(f"[{symbol}] consensus={result['consensus_display']} "
              f"buckets={result['ordinal_context']}")


if __name__ == "__main__":
    main()
