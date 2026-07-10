"""Case studies are reproducible, honest, and firewall-safe (part-010).

Each case is loaded through the shared runner. We lock:
- reproducibility (run twice, identical),
- the key conclusion (aggregate_neutral consensus + divergence bucket) matches the
  doc's front-matter comment (no drift between prose and code),
- every case doc has a "哪裡不能信" / limitations section,
- raw metric numbers never leak into the narrative.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from case_studies.cases import ALL_CASES
from case_studies.runner import run_case

_CASE_DIR = pathlib.Path(__file__).resolve().parent.parent / "case_studies"

# doc filename per case label prefix
_DOCS = {
    "CASE A": "case_a_etf_discount.md",
    "CASE B": "case_b_price_hike.md",
    "CASE C": "case_c_premium_chase.md",
}


def _existing_cases():
    out = []
    for spec in ALL_CASES:
        prefix = spec.label.split(" —")[0]
        doc = _CASE_DIR / _DOCS[prefix]
        if doc.exists():
            out.append((spec, doc))
    return out


_CASES = _existing_cases()
_IDS = [c[0].label.split(" —")[0] for c in _CASES]


@pytest.mark.parametrize("spec,doc", _CASES, ids=_IDS)
def test_case_is_reproducible(spec, doc):
    a = run_case(spec)
    b = run_case(spec)
    assert a == b


@pytest.mark.parametrize("spec,doc", _CASES, ids=_IDS)
def test_case_conclusion_matches_doc(spec, doc):
    r = run_case(spec)
    text = doc.read_text(encoding="utf-8")
    m = re.search(
        r"aggregate_neutral_consensus:\s*(\w+)\s*\|\s*divergence_bucket:\s*(\w+)", text
    )
    assert m, f"{doc.name} missing case-id front-matter comment"
    assert r.consensus_by_mode["aggregate_neutral"] == m.group(1)
    assert r.divergence_bucket == m.group(2)


@pytest.mark.parametrize("spec,doc", _CASES, ids=_IDS)
def test_case_doc_has_limitations_section(spec, doc):
    text = doc.read_text(encoding="utf-8")
    assert "哪裡不能信" in text, f"{doc.name} must keep the mandatory limitations section"


@pytest.mark.parametrize("spec,doc", _CASES, ids=_IDS)
def test_case_narrative_does_not_leak_raw_numbers(spec, doc):
    r = run_case(spec)
    for value in r.raw_metrics.values():
        assert str(value) not in r.narrative_md
