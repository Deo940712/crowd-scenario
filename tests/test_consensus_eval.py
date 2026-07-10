"""The consensus-model evaluation harness is reproducible (part-008 slice-003).

Locks that the comparison matrix is deterministic (same bytes every run) and that its
key structural findings hold — without asserting any specific "right answer" beyond the
net-sign rule the engine already guarantees. The harness lives in tools/ (not an
installed package), so it is loaded from its path.
"""

from __future__ import annotations

import importlib.util
import pathlib

_HARNESS = pathlib.Path(__file__).resolve().parent.parent / "tools" / "eval_consensus.py"


def _load():
    spec = importlib.util.spec_from_file_location("eval_consensus", _HARNESS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_is_reproducible():
    mod = _load()
    assert mod.build_matrix() == mod.build_matrix()


def test_matrix_reports_neutral_hash_independence():
    mod = _load()
    matrix = mod.build_matrix()
    assert "hash-independence (all cases): True" in matrix


def test_neutral_model_never_contradicts_its_own_majority():
    # For every case, aggregate_neutral's emitted direction must match its persona net
    # sign rule (this is the "explainable from personas" property).
    mod = _load()
    for _label, pack, symbol, metrics, _intended in mod._CASES:
        consensus, net = mod._run(pack, symbol, metrics, "aggregate_neutral")
        assert mod._agrees_with_majority(consensus, net)
