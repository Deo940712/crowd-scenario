"""The real-data worked example runs, stays categorical, and never leaks raw numbers.

Locks part-005: the firewall must hold even when a real data layer feeds raw metrics in.
The example is loaded from its file path (examples/ is not an installed package).
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_EXAMPLE_PATH = pathlib.Path(__file__).resolve().parent.parent / "examples" / "real_data.py"


def _load_example():
    spec = importlib.util.spec_from_file_location("real_data_example", _EXAMPLE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def example():
    return _load_example()


def test_example_runs_and_emits_categorical(example):
    result = example.rehearse("0056", "rate_cut")
    assert result["crowd_consensus"] in ("negative", "neutral", "positive")
    assert result["consensus_display"] in ("bearish", "neutral", "bullish")


def test_example_does_not_leak_raw_scores(example):
    result = example.rehearse("0056", "rate_cut")
    raw = example.fetch_metrics("0056")
    blob = result["narrative_md"] + str(result["crowd_consensus"])
    for value in raw.values():
        assert str(value) not in blob  # e.g. "-0.6" / "8.5" must not survive


def test_example_is_deterministic(example):
    assert example.rehearse("0056", "rate_cut") == example.rehearse("0056", "rate_cut")
