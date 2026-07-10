"""CLI behaviour: argument wiring for `run` — --consensus-mode (part-001/slice-002)
and --metrics (part-002/slice-001).

These drive the parser + command functions directly (no subprocess) and read the
JSON that `cmd_run` prints, so they lock the CLI contract without a shell (which also
sidesteps PowerShell/bash JSON-quoting differences).
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


def test_run_defaults_to_aggregate_neutral_mode(capsys):
    # part-013: the public default is aggregate_neutral since 0.2.0.
    data = _run_json(capsys, ["run", "--symbol", "0056", "--scenario", "0056_cut"])
    assert data["consensus_mode"] == "aggregate_neutral"
    assert data["crowd_consensus"] in ("negative", "neutral", "positive")


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


# --- --metrics self-service input (part-002/slice-001) -----------------------------

_CUSTOM = '{"discount_premium": -1.5, "yield": 9.0}'


def test_run_accepts_custom_metrics(capsys):
    data = _run_json(
        capsys,
        ["run", "--symbol", "CUSTOM", "--scenario", "evt", "--metrics", _CUSTOM],
    )
    # a real rehearsal came out for a symbol that has no fixture
    assert data["crowd_consensus"] in ("negative", "neutral", "positive")
    assert data["seed_id"].startswith("seed_CUSTOM_")


def test_run_metrics_override_beats_fixture(capsys):
    # 0056 HAS a fixture; --metrics must win, producing a different seed than the fixture.
    fixture = _run_json(capsys, ["run", "--symbol", "0056", "--scenario", "evt"])
    override = _run_json(
        capsys, ["run", "--symbol", "0056", "--scenario", "evt", "--metrics", _CUSTOM]
    )
    assert override["seed_id"] != fixture["seed_id"]


def test_run_invalid_metrics_json_is_clean_error(capsys):
    rc = main(["run", "--symbol", "X", "--scenario", "evt", "--metrics", "{bad json"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "error" in err.lower()
    assert "Traceback" not in err


def test_run_missing_metric_is_clean_error(capsys):
    # stock pack needs discount_premium AND yield; omit yield.
    rc = main(
        ["run", "--symbol", "X", "--scenario", "evt", "--metrics", '{"discount_premium": -0.6}']
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert "error" in err.lower()
    assert "Traceback" not in err


def test_run_unknown_symbol_without_metrics_warns_but_runs(capsys):
    rc = main(["run", "--symbol", "NOFIXTURE", "--scenario", "evt"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "warning" in captured.err.lower()
    # still produced a valid artifact on stdout
    assert json.loads(captured.out)["crowd_consensus"] in ("negative", "neutral", "positive")


def test_run_custom_metrics_do_not_leak_raw_numbers(capsys):
    data = _run_json(
        capsys,
        ["run", "--symbol", "CUSTOM", "--scenario", "evt", "--metrics", _CUSTOM],
    )
    blob = json.dumps(data, ensure_ascii=False)
    # the raw input numbers must not survive into the emitted artifact
    assert "-1.5" not in blob
    assert "9.0" not in blob


# --- run --sweep (part-007/slice-002) ----------------------------------------------


def test_run_sweep_outputs_all_horizon_intensity_cells(capsys):
    assert main(["run", "--symbol", "0056", "--scenario", "evt", "--sweep"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert isinstance(rows, list)
    cells = {(r["horizon"], r["intensity"]) for r in rows}
    assert cells == {
        (h, i) for h in ("intraday", "swing", "long") for i in ("mild", "severe")
    }
    assert len(rows) == 6


def test_run_sweep_is_deterministic(capsys):
    main(["run", "--symbol", "0056", "--scenario", "evt", "--sweep"])
    a = capsys.readouterr().out
    main(["run", "--symbol", "0056", "--scenario", "evt", "--sweep"])
    b = capsys.readouterr().out
    assert a == b


# --- software_migration domain via CLI (part-012/slice-002) ------------------------


def test_run_software_migration_domain(capsys):
    data = _run_json(
        capsys,
        ["run", "--domain", "software_migration", "--symbol", "big_rewrite",
         "--scenario", "v9_rewrite"],
    )
    assert data["domain"] == "software_migration"
    assert data["consensus_display"] in ("resist", "wait", "adopt")


def test_run_software_migration_sweep(capsys):
    assert main([
        "run", "--domain", "software_migration", "--symbol", "big_rewrite",
        "--scenario", "v9_rewrite", "--sweep",
    ]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 6
    assert all(r["domain"] == "software_migration" for r in rows)


# --- --metrics value validation (part-014/slice-003) -------------------------------
#
# json.loads accepts NaN/Infinity as float literals, and a string/bool value would only
# blow up deep inside a bucket_fn with a raw TypeError traceback. _parse_metrics must
# reject any non-finite / non-numeric value up front with a clean exit-2 error.


def _bad_metrics_is_clean_error(capsys, metrics: str) -> None:
    rc = main(["run", "--symbol", "X", "--scenario", "evt", "--metrics", metrics])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.err.lower().startswith("error")
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_run_string_metric_value_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '{"discount_premium": "bad", "yield": 8.5}')


def test_run_null_metric_value_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '{"discount_premium": null, "yield": 8.5}')


def test_run_bool_metric_value_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '{"discount_premium": true, "yield": 8.5}')


def test_run_nan_metric_value_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '{"discount_premium": NaN, "yield": 8.5}')


def test_run_infinity_metric_value_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '{"discount_premium": Infinity, "yield": 8.5}')


def test_run_array_metrics_payload_is_clean_error(capsys):
    _bad_metrics_is_clean_error(capsys, '[1, 2, 3]')


def test_run_valid_numeric_metrics_still_work(capsys):
    data = _run_json(
        capsys,
        ["run", "--symbol", "X", "--scenario", "evt",
         "--metrics", '{"discount_premium": -0.6, "yield": 8.5}'],
    )
    assert data["crowd_consensus"] in ("negative", "neutral", "positive")
