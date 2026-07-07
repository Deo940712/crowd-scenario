"""Narrator backends: firewall scanner + fusion (2 writers + 1 judge) with fakes.

Locks the fusion contract WITHOUT a real LLM: the injected model callables are fakes
(text-in/text-out). The load-bearing invariants:
- the firewall scanner catches numeric tokens + order language, and passes clean prose,
- the deterministic narrator is byte-identical to the engine's original output,
- fusion screens EVERY model output (both writers AND the judge) through the scanner,
- fusion falls back to the deterministic narrator when nothing survives,
- fusion NEVER changes the engine's categorical consensus or any persona stance.
"""

from __future__ import annotations

from crowdscenario import STOCK_TW, make_seed, run_scenario
from crowdscenario.narrator import (
    DeterministicNarrator,
    FusionNarrator,
    is_clean,
    scan_violations,
)
from crowdscenario.narrator.base import EngineFacts, PersonaFact

# --- firewall scanner ---------------------------------------------------------------


def test_scan_passes_clean_conditional_prose():
    assert is_clean("若這類人格可能傾向續抱不動,氣氛熱絡。")
    assert scan_violations("看板風向轉多、互相勸退。") == ()


def test_scan_catches_currency_tokens():
    assert scan_violations("NT$100 進場")
    assert scan_violations("成本 300 元")
    assert scan_violations("台幣 500")


def test_scan_catches_percent_and_yield():
    assert scan_violations("殖利率 8.5%")
    assert scan_violations("報酬率:12")


def test_scan_catches_price_nav_and_bare_decimal():
    assert scan_violations("淨值 15.2")
    assert scan_violations("目標價:50")
    assert scan_violations("大約 3.14 的水準")


def test_scan_catches_order_language():
    assert scan_violations("建議買進這檔")
    assert scan_violations("委託單已送出")
    assert scan_violations("you should buy it")


def test_deterministic_narrative_is_clean():
    md = run_scenario(_seed()).narrative_md
    assert is_clean(md)


# --- helpers ------------------------------------------------------------------------


def _seed():
    return make_seed("0056", {"discount_premium": -0.6, "yield": 8.5}, "0056_cut", pack=STOCK_TW)


def _facts():
    return EngineFacts(
        label="evt",
        consensus="negative",
        consensus_display="bearish",
        frame="波段",
        intensity_zh="溫和",
        personas=(PersonaFact("p", "存股族", -1, "續抱不動"),),
        reaction_chain="1. **存股族** 最先動作 —— 續抱不動",
    )


def _const(text):
    return lambda _prompt: text


# --- deterministic narrator ---------------------------------------------------------


def test_deterministic_narrator_matches_engine_output():
    # The engine delegates to DeterministicNarrator by default; an explicit instance
    # must produce the exact same narrative for the same seed.
    default = run_scenario(_seed())
    explicit = run_scenario(_seed(), narrator=DeterministicNarrator())
    assert default.narrative_md == explicit.narrative_md


# --- fusion: happy path -------------------------------------------------------------


def test_fusion_judge_wins_when_all_clean():
    clean = "若這類人格可能傾向續抱不動,情境偏保守。"
    fusion = FusionNarrator(
        writer_a=_const("候選甲:條件式敘事一。"),
        writer_b=_const("候選乙:條件式敘事二。"),
        judge=_const(clean),
    )
    result = fusion.render(_facts())
    assert result.narrative_md == clean
    assert result.backend == "fusion:judge"


def test_fusion_rejects_dirty_writer_but_keeps_clean_one():
    clean = "乾淨的條件式敘事。"
    fusion = FusionNarrator(
        writer_a=_const("這檔目標價 50 元,快買。"),  # dirty: numeric + order
        writer_b=_const(clean),
        judge=_const("殖利率 8%"),  # judge dirty -> fall back to surviving writer
    )
    result = fusion.render(_facts())
    assert result.narrative_md == clean
    assert result.backend == "fusion:writer"
    assert "writer_a:rejected" in result.notes
    assert "writer_b:accepted" in result.notes


def test_fusion_falls_back_when_no_writer_survives():
    fusion = FusionNarrator(
        writer_a=_const("NT$100"),  # dirty
        writer_b=_const("委託單"),  # dirty
        judge=_const("irrelevant"),
    )
    result = fusion.render(_facts())
    # fallback == deterministic narrative for the same facts
    assert result.backend == "fusion:fallback"
    assert result.narrative_md == DeterministicNarrator().render(_facts()).narrative_md


def test_fusion_falls_back_when_model_raises():
    def boom(_prompt):
        raise RuntimeError("model down")

    fusion = FusionNarrator(writer_a=boom, writer_b=boom, judge=boom)
    result = fusion.render(_facts())
    assert result.backend == "fusion:fallback"


def test_fusion_judge_output_is_rescreened():
    # Both writers clean, but the judge injects a numeric leak -> judge output rejected,
    # falls back to a clean writer candidate, never emitting the dirty judge text.
    fusion = FusionNarrator(
        writer_a=_const("乾淨敘事甲。"),
        writer_b=_const("乾淨敘事乙。"),
        judge=_const("融合版:目標價 42。"),
    )
    result = fusion.render(_facts())
    assert is_clean(result.narrative_md)
    assert "42" not in result.narrative_md


# --- fusion: firewall invariant end-to-end ------------------------------------------


def test_fusion_never_changes_consensus_or_stance():
    baseline = run_scenario(_seed())
    fusion = FusionNarrator(
        writer_a=_const("完全不同的條件式敘事。"),
        writer_b=_const("另一版敘事。"),
        judge=_const("裁判選定的敘事。"),
    )
    fused = run_scenario(_seed(), narrator=fusion)
    # Prose differs, but the categorical facts are identical to the engine's decision.
    assert fused.crowd_consensus == baseline.crowd_consensus
    assert fused.persona_samples == baseline.persona_samples
    assert fused.narrative_md != baseline.narrative_md
