"""Adversarial firewall corpus (part-009): threat-model-driven reject/allow cases.

The scanner is a deterministic defense-in-depth filter, not a complete semantic safety
system. These lock its real boundary: every must_reject line is caught, every must_allow
line (plus every shipped pack voice) passes clean. T4 (semantic advice) and T5 (encoded
payloads) are deliberately absent — they are documented limitations, not targets.
"""

from __future__ import annotations

import pathlib

import pytest

from crowdscenario import PRODUCT_LAUNCH, STOCK_TW, scan_violations

_CORPUS = pathlib.Path(__file__).resolve().parent / "firewall_corpus"


def _load(name: str) -> list[str]:
    lines = (_CORPUS / name).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


_MUST_REJECT = _load("must_reject.txt")
_MUST_ALLOW = _load("must_allow.txt")


def _all_pack_voices() -> list[str]:
    out: list[str] = []
    for pack in (STOCK_TW, PRODUCT_LAUNCH):
        for stances in pack.voice.values():
            out.extend(stances.values())
        for stances in getattr(pack, "voice_variants", {}).values():
            for variants in stances.values():
                out.extend(variants)
    return out


_PACK_VOICES = _all_pack_voices()


@pytest.mark.parametrize("line", _MUST_ALLOW, ids=range(len(_MUST_ALLOW)))
def test_must_allow_corpus_is_clean(line):
    assert scan_violations(line) == (), f"false positive on: {line!r}"


@pytest.mark.parametrize("voice", _PACK_VOICES, ids=range(len(_PACK_VOICES)))
def test_all_shipped_pack_voices_are_clean(voice):
    # Zero-false-positive regression: no persona voice or variant may be flagged.
    assert scan_violations(voice) == (), f"scanner flags a legit pack voice: {voice!r}"


@pytest.mark.parametrize("line", _MUST_REJECT, ids=range(len(_MUST_REJECT)))
def test_must_reject_corpus_is_flagged(line):
    assert scan_violations(line) != (), f"missed violation on: {line!r}"
