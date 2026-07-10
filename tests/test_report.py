"""The static HTML report is deterministic, complete, honest, and XSS-safe (part-011).

The generator lives in tools/ (not an installed package), so it is loaded from its path.
A sweep is produced through the real CLI, then rendered; we lock reproducibility, the six
cells, the disclaimer, no-raw-number leak, and HTML-escaping of a hostile scenario label.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib

_REPORT = pathlib.Path(__file__).resolve().parent.parent / "tools" / "report.py"


def _load_report():
    spec = importlib.util.spec_from_file_location("report_tool", _REPORT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sweep(scenario: str = "evt") -> list[dict]:
    from crowdscenario.cli import main as cli_main

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli_main(["run", "--symbol", "0056", "--scenario", scenario, "--sweep"])
    return json.loads(buf.getvalue())


def test_report_is_deterministic():
    mod = _load_report()
    rows = _sweep()
    assert mod.build_html(rows) == mod.build_html(rows)


def test_report_contains_all_six_cells():
    mod = _load_report()
    html_out = mod.build_html(_sweep())
    for h in ("intraday", "swing", "long"):
        assert h in html_out
    for i in ("mild", "severe"):
        assert i in html_out


def test_report_has_disclaimer_and_no_raw_numbers():
    mod = _load_report()
    html_out = mod.build_html(_sweep())
    assert "not a forecast" in html_out
    # the 0056 fixture's raw metrics must not appear in the rendered report
    assert "-0.6" not in html_out
    assert "8.5" not in html_out


def test_report_escapes_hostile_symbol():
    # A hostile --symbol flows into seed_id, which the report renders — it must be escaped.
    import contextlib as _c
    import io as _io

    from crowdscenario.cli import main as cli_main

    mod = _load_report()
    buf = _io.StringIO()
    with _c.redirect_stdout(buf):
        cli_main(["run", "--symbol", "<script>alert(1)</script>", "--scenario", "evt", "--sweep"])
    rows = json.loads(buf.getvalue())
    html_out = mod.build_html(rows)
    assert "<script>alert(1)</script>" not in html_out
    assert "&lt;script&gt;" in html_out
