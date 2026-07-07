"""CLI behaviour: argument wiring for `run`, including --consensus-mode (part-001/slice-002).

These drive the parser + command functions directly (no subprocess) and read the
JSON that `cmd_run` prints, so they lock the CLI contract without a shell.
"""

from __future__ import annotations

import json

import pytest

from crowdscenario.cli import build_parser, main


def _run_json(capsys, argv: list[str]) -> dict:
    assert main(argv) == 0
    out = capsys.readouterr().out
    return json.loads(out)


# --- --consensus-mode wiring -------------------------------------------------------


def test_run_defaults_to_hashed_mode(capsys):
    data = _run_json(capsys, ["run", "--symbol", "0056", "--scenario", "0056_cut"])
    assert data["consensus_mode"] == "hashed"
    # hashed default for this fixture has always been positive
    assert data["crowd_consensus"] == "positive"


def test_run_accepts_explicit_hashed(capsys):
    data = _run_json(
        capsys,
        ["run", "--symbol", "0056", "--scenario", "0056_cut", "--consensus-mode", "hashed"],
    )
    assert data["consensus_mode"] == "hashed"
    assert data["crowd_consensus"] == "positive"


# PRODUCT redesign/redesign is a fixture where the two modes DISAGREE: the seed hash
# rolls one direction while the persona majority (net) sits at another. Exact directions
# depend on the seed hash, so these tests assert the *rule*, not pinned dice values.
_DISAGREE_ARGS = [
    "run", "--domain", "product_launch", "--symbol", "redesign", "--scenario", "redesign",
]


def _expected_from_net(net: int) -> str:
    return "positive" if net > 1 else ("negative" if net < -1 else "neutral")


def test_run_aggregate_mode_follows_net_sign_rule(capsys):
    data = _run_json(capsys, [*_DISAGREE_ARGS, "--consensus-mode", "aggregate"])
    assert data["consensus_mode"] == "aggregate"
    net = sum(s["stance"] for s in data["persona_samples"])
    assert data["crowd_consensus"] == _expected_from_net(net)


def test_run_mode_changes_only_consensus_not_samples(capsys):
    # Same seed, two modes: persona stances are identical (decided pre-aggregate);
    # only the emitted crowd_consensus direction may differ. This fixture is chosen so
    # the two modes actually diverge, proving the flag has a real effect.
    hashed = _run_json(capsys, [*_DISAGREE_ARGS, "--consensus-mode", "hashed"])
    aggregate = _run_json(capsys, [*_DISAGREE_ARGS, "--consensus-mode", "aggregate"])
    assert hashed["persona_samples"] == aggregate["persona_samples"]
    assert hashed["crowd_consensus"] != aggregate["crowd_consensus"]
    net = sum(s["stance"] for s in aggregate["persona_samples"])
    assert aggregate["crowd_consensus"] == _expected_from_net(net)


def test_parser_rejects_unknown_consensus_mode():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "--consensus-mode", "magic"])


def test_verify_has_no_consensus_mode_flag():
    # verify is a pure determinism check; --consensus-mode is intentionally not added.
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["verify", "--consensus-mode", "aggregate"])
