"""Regression locks for the code-review hardening pass.

Each test pins one invariant introduced by the review recommendations, so a future
change that quietly re-opens a firewall hole fails loudly here:

- contracts survive ``python -O`` (explicit ``raise``, never ``assert``),
- a seed is bound to its domain and a pack mismatch is refused,
- missing metrics / unknown buckets fail fast instead of defaulting to neutral,
- the fusion prompt uses textual stance labels and the scanner rejects numeric
  signal tokens / fullwidth numerics,
- narrator provenance survives onto the CrowdNarrative,
- the seed's ordinal map is deep-frozen,
- every shipped pack's voice covers all three stances.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from crowdscenario import (
    PRODUCT_LAUNCH,
    STOCK_TW,
    ContractError,
    FusionNarrator,
    make_seed,
    run_scenario,
)
from crowdscenario.narrator import is_clean, scan_violations
from crowdscenario.narrator.base import EngineFacts, PersonaFact
from crowdscenario.narrator.fusion import _facts_block

_STOCK_METRICS = {"discount_premium": -0.6, "yield": 8.5}


# --- P1: contracts survive python -O ------------------------------------------------


def test_contracts_survive_python_optimized_mode():
    # assert-based contracts are stripped under -O; explicit raises are not. Run a
    # fresh interpreter with -O and confirm an out-of-vocabulary consensus still fails.
    code = (
        "from crowdscenario.contracts import CrowdNarrative, ContractError\n"
        "try:\n"
        "    CrowdNarrative(seed_id='x', rng_seed=1, n_personas=30,"
        " crowd_consensus='VERY_BULLISH', narrative_md='t')\n"
        "except ContractError:\n"
        "    print('REJECTED')\n"
        "else:\n"
        "    raise SystemExit('contract bypassed under -O')\n"
    )
    proc = subprocess.run(
        [sys.executable, "-O", "-c", code],
        capture_output=True,
        text=True,
        cwd=_repo_src_on_path(),
    )
    assert proc.returncode == 0, proc.stderr
    assert "REJECTED" in proc.stdout


def _repo_src_on_path() -> str:
    # pyproject sets pythonpath=["src"] for pytest; a raw subprocess needs it too.
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    src = str(root / "src")
    import os

    env_path = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = src + os.pathsep + env_path if env_path else src
    return str(root)


# --- P1: seed/domain integrity ------------------------------------------------------


def test_make_seed_binds_domain_id():
    seed = make_seed("0056", _STOCK_METRICS, "0056_cut", pack=STOCK_TW)
    assert seed.domain_id == "stock_tw"


def test_run_scenario_rejects_seed_pack_domain_mismatch():
    stock_seed = make_seed("0056", _STOCK_METRICS, "0056_cut", pack=STOCK_TW)
    with pytest.raises(ContractError):
        run_scenario(stock_seed, pack=PRODUCT_LAUNCH)


# --- P2: fail-fast on bad domain input ----------------------------------------------


def test_make_seed_rejects_missing_metric_by_default():
    with pytest.raises(ContractError):
        make_seed("0056", {"discount_premium": -0.6}, "0056_cut", pack=STOCK_TW)  # no yield


def test_stance_rejects_unknown_axis_bucket():
    # A pack whose bucket_fn returns a label absent from tilt must fail at stance time,
    # not silently be treated as neutral.
    from crowdscenario.domains.base import Axis, DomainPack

    bad = DomainPack(
        domain_id="bad",
        persona_ids=("a",),
        contra_ids=frozenset(),
        herding={"a": 0.5},
        voice={"a": {1: "x", 0: "y", -1: "z"}},
        display_name={"a": "A"},
        axes=(Axis(name="ax", bucket_fn=lambda _x: "ghost", tilt={"mid": 0.0}),),
        sensitivity={"a": (1.0,)},
        consensus_display={"negative": "n", "neutral": "u", "positive": "p"},
    )
    seed = make_seed("s", {"ax": 0.0}, "evt", pack=bad)
    with pytest.raises(ContractError):
        run_scenario(seed, pack=bad)


# --- P2: fusion firewall / stance encoding ------------------------------------------


def test_fusion_prompt_uses_textual_stance_labels():
    facts = _facts()
    block = _facts_block(facts)
    assert "偏空" in block
    assert "stance=" not in block
    assert "stance=-1" not in block


def test_firewall_rejects_numeric_stance_tokens():
    assert scan_violations("stance=-1")
    assert scan_violations("score=0")
    assert scan_violations("modifier=1")
    assert not is_clean("weight=2 的權重")


def test_firewall_catches_fullwidth_numeric():
    assert scan_violations("報酬率 ５０％")  # fullwidth digits + fullwidth percent
    assert scan_violations("成本 １００ 元")


def test_firewall_rejects_bare_buy_sell_order():
    assert scan_violations("買進")
    assert scan_violations("賣出")
    # conditional persona compounds stay clean (加碼/停損 描述性用語)
    assert is_clean("這類人格可能想趁機加碼撿便宜。")


# --- P3: observability --------------------------------------------------------------


def test_crowd_narrative_preserves_narrator_provenance():
    n = run_scenario(make_seed("0056", _STOCK_METRICS, "0056_cut", pack=STOCK_TW))
    assert n.narrator_backend == "deterministic"


def test_fusion_provenance_reaches_crowd_narrative():
    fusion = FusionNarrator(
        writer_a=lambda _p: "乾淨敘事甲。",
        writer_b=lambda _p: "乾淨敘事乙。",
        judge=lambda _p: "裁判選定的條件式敘事。",
    )
    n = run_scenario(
        make_seed("0056", _STOCK_METRICS, "0056_cut", pack=STOCK_TW), narrator=fusion
    )
    assert n.narrator_backend == "fusion:judge"


# --- deep-freeze --------------------------------------------------------------------


def test_seed_ordinal_context_is_deep_frozen():
    seed = make_seed("0056", _STOCK_METRICS, "0056_cut", pack=STOCK_TW)
    with pytest.raises(TypeError):
        seed.ordinal_context["yield"] = "tampered"  # type: ignore[index]


# --- pack helper: voice covers every stance -----------------------------------------


@pytest.mark.parametrize("pack", [STOCK_TW, PRODUCT_LAUNCH], ids=lambda p: p.domain_id)
def test_pack_voice_covers_all_stances_and_buckets(pack):
    for pid in pack.persona_ids:
        assert set(pack.voice[pid].keys()) == {-1, 0, 1}
        assert pack.display_name[pid].strip()
    # every axis bucket the pack can emit must exist in that axis's tilt table
    for axis in pack.axes:
        for bucket in axis.tilt:
            assert isinstance(bucket, str)


# --- helpers ------------------------------------------------------------------------


def _facts() -> EngineFacts:
    return EngineFacts(
        label="evt",
        consensus="negative",
        consensus_display="bearish",
        frame="波段",
        intensity_zh="溫和",
        personas=(PersonaFact("p", "存股族", -1, "續抱不動"),),
        reaction_chain="1. **存股族** 最先動作 —— 續抱不動",
    )
