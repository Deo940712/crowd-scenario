"""Consensus-model evaluation harness (part-008).

Runs a fixed case corpus (two shipped packs × positive / negative / neutral-ish
scenarios) through all three consensus models and reports a comparison matrix:

    hashed | aggregate | aggregate_neutral

For each case it records the emitted consensus per model, the persona net stance (an
INTERNAL statistic for evaluation only — never emitted on an artifact), whether each
model's direction agrees with the persona majority, and hash-independence for the
neutral model. Deterministic and offline; produces the same Markdown every run.

This is NOT a backtest and makes no accuracy claim. It measures semantic consistency,
neutral stability, and explainability — the criteria in the PART DESIGN.

    PowerShell:  $env:PYTHONPATH='src'; python tools/eval_consensus.py
    bash:        PYTHONPATH=src python tools/eval_consensus.py
"""

from __future__ import annotations

from crowdscenario import STOCK_TW, make_seed, run_scenario
from crowdscenario.domains.base import DomainPack
from crowdscenario.domains.product import PRODUCT_LAUNCH

_MODES = ("hashed", "aggregate", "aggregate_neutral")

# (label, pack, symbol, metrics, intended_direction)
# intended_direction is the human reading of the buckets — used only to flag
# counter-intuitive rows, NEVER to branch engine logic.
_CASES: list[tuple[str, DomainPack, str, dict[str, float], str]] = [
    ("stock cheap+hi-yield", STOCK_TW, "cheap_hi",
     {"discount_premium": -1.5, "yield": 9.0}, "positive"),
    ("stock rich+lo-yield", STOCK_TW, "rich_lo",
     {"discount_premium": 1.4, "yield": 2.0}, "negative"),
    ("stock fair+mid-yield", STOCK_TW, "fair_mid",
     {"discount_premium": 0.0, "yield": 4.5}, "neutral"),
    ("product hike+low-value", PRODUCT_LAUNCH, "hike_lowval",
     {"price_change": 0.4, "value_delta": -0.4, "switching_cost": 0.6}, "negative"),
    ("product value+flat-price", PRODUCT_LAUNCH, "value_flat",
     {"price_change": 0.0, "value_delta": 0.8, "switching_cost": 0.2}, "positive"),
    ("product neutral-mid", PRODUCT_LAUNCH, "neutral_mid",
     {"price_change": 0.0, "value_delta": 0.0, "switching_cost": 0.4}, "neutral"),
]


def _run(pack: DomainPack, symbol: str, metrics: dict[str, float], mode: str,
         scenario: str = "evt") -> tuple[str, int]:
    seed = make_seed(symbol, metrics, scenario, pack=pack)
    result = run_scenario(seed, pack=pack, consensus_mode=mode)
    net = sum(s.stance for s in result.persona_samples)
    return result.crowd_consensus, net


def _agrees_with_majority(consensus: str, net: int) -> bool:
    majority = "positive" if net > 0 else ("negative" if net < 0 else "neutral")
    return consensus == majority


def _hash_independent(pack: DomainPack, symbol: str, metrics: dict[str, float]) -> bool:
    a, _ = _run(pack, symbol, metrics, "aggregate_neutral", scenario="evtA")
    b, _ = _run(pack, symbol, metrics, "aggregate_neutral", scenario="evtB")
    return a == b


def build_matrix() -> str:
    lines: list[str] = []
    lines.append("| case | intended | hashed | aggregate | aggregate_neutral | net |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    counter_intuitive = {m: 0 for m in _MODES}
    majority_disagree = {m: 0 for m in _MODES}
    for label, pack, symbol, metrics, intended in _CASES:
        cells: dict[str, str] = {}
        net_ref = 0
        for mode in _MODES:
            consensus, net = _run(pack, symbol, metrics, mode)
            cells[mode] = consensus
            if mode == "aggregate_neutral":
                net_ref = net
            if intended != "neutral" and consensus != intended:
                counter_intuitive[mode] += 1
            if not _agrees_with_majority(consensus, net):
                majority_disagree[mode] += 1
        lines.append(
            f"| {label} | {intended} | {cells['hashed']} | {cells['aggregate']} "
            f"| {cells['aggregate_neutral']} | {net_ref:+d} |"
        )

    lines.append("")
    lines.append("### Summary (over the case corpus)")
    lines.append("")
    lines.append("| metric | hashed | aggregate | aggregate_neutral |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(
        f"| counter-intuitive rows (directional cases) | {counter_intuitive['hashed']} "
        f"| {counter_intuitive['aggregate']} | {counter_intuitive['aggregate_neutral']} |"
    )
    lines.append(
        f"| disagrees with persona majority | {majority_disagree['hashed']} "
        f"| {majority_disagree['aggregate']} | {majority_disagree['aggregate_neutral']} |"
    )
    hash_indep = all(_hash_independent(p, s, m) for _, p, s, m, _ in _CASES)
    lines.append("")
    lines.append(f"aggregate_neutral hash-independence (all cases): {hash_indep}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_matrix())
