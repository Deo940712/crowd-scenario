"""Static HTML comparison report (part-011).

Turns a ``crowdscenario run --sweep`` JSON array (six horizon × intensity cells) into a
single self-contained HTML file: a 3×2 grid of crowd stances, the persona stance
distribution as COLOUR CATEGORIES (never a numeric bar — the firewall extends to the
visual layer), and a fixed rehearsal-not-forecast disclaimer.

Deterministic and offline. All dynamic text is HTML-escaped (scenario labels are
user-supplied), so the report is XSS-safe. stdlib only — no template engine, no CDN.

    PowerShell:  $env:PYTHONPATH="src;$PWD"
                 python -m crowdscenario run --symbol 0056 --scenario evt --sweep |
                     python tools/report.py --out report.html
    bash:        PYTHONPATH="src:$PWD" \\
                 python -m crowdscenario run --symbol 0056 --scenario evt --sweep |
                     python tools/report.py --out report.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys

_HORIZONS = ("intraday", "swing", "long")
_INTENSITIES = ("mild", "severe")
# Text-labelled colours (not colour-only, and never a numeric bar): stance category.
_STANCE_CLASS = {-1: "neg", 0: "neu", 1: "pos"}
_STANCE_LABEL = {-1: "−", 0: "0", 1: "+"}

_CSS = """
body{font-family:system-ui,"Segoe UI",sans-serif;margin:2rem;color:#1a1a1a;background:#fafafa}
h1{font-size:1.3rem;margin:0 0 .2rem}.sub{color:#666;margin:0 0 1.2rem;font-size:.9rem}
table{border-collapse:collapse;margin:1rem 0}
th,td{border:1px solid #ddd;padding:.5rem .7rem;text-align:left;vertical-align:top}
th{background:#f0f0f0}
.c-positive{background:#e7f5e9}.c-negative{background:#fdeaea}.c-neutral{background:#f3f3f3}
.stance{display:inline-block;width:1.1rem;height:1.1rem;line-height:1.1rem;text-align:center;
        border-radius:3px;font-weight:700;margin:1px;font-size:.75rem}
.neg{background:#e53935;color:#fff}.neu{background:#bdbdbd;color:#111}
.pos{background:#43a047;color:#fff}
.legend span{margin-right:1rem}
.panel{margin:1rem 0;padding:.8rem 1rem;background:#fff;border:1px solid #eee}
.disclaimer{margin-top:2rem;padding:.8rem 1rem;background:#fffbe6;border:1px solid #f0e0a0;
            font-size:.85rem}
""".strip()


def _cell_class(consensus: str) -> str:
    return {"positive": "c-positive", "negative": "c-negative"}.get(consensus, "c-neutral")


def _grid_html(rows: list[dict]) -> str:
    by_cell = {(r["horizon"], r["intensity"]): r for r in rows}
    out = ["<table><tr><th></th>"]
    for i in _INTENSITIES:
        out.append(f"<th>{html.escape(i)}</th>")
    out.append("</tr>")
    for h in _HORIZONS:
        out.append(f"<tr><th>{html.escape(h)}</th>")
        for i in _INTENSITIES:
            r = by_cell.get((h, i))
            if r is None:
                out.append("<td>—</td>")
                continue
            cons = r["crowd_consensus"]
            disp = r.get("consensus_display", cons)
            out.append(
                f'<td class="{_cell_class(cons)}"><b>{html.escape(str(disp))}</b>'
                f'<br><small>{html.escape(cons)}</small></td>'
            )
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)


def _distribution_html(rows: list[dict]) -> str:
    # Use the default cell (swing/mild) for the persona distribution snapshot.
    sample = next(
        (r for r in rows if r["horizon"] == "swing" and r["intensity"] == "mild"), rows[0]
    )
    chips = []
    for s in sample.get("persona_samples", []):
        cls = _STANCE_CLASS.get(s["stance"], "neu")
        lab = _STANCE_LABEL.get(s["stance"], "0")
        title = html.escape(s["archetype_id"])
        chips.append(f'<span class="stance {cls}" title="{title}">{lab}</span>')
    return (
        '<div class="panel"><b>Persona distribution</b> '
        f'(cell: {html.escape(sample["horizon"])}/{html.escape(sample["intensity"])}) — '
        "colour categories, not scores:<br>" + "".join(chips) + "</div>"
    )


def build_html(rows: list[dict]) -> str:
    if not rows:
        raise ValueError("empty sweep: expected a JSON array of cells")
    first = rows[0]
    domain = html.escape(str(first.get("domain", "")))
    seed_id = html.escape(str(first.get("seed_id", "")))
    mode = html.escape(str(first.get("consensus_mode", "")))
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>crowd-scenario report — {domain}</title><style>{_CSS}</style></head><body>"
        f"<h1>crowd-scenario report — {domain}</h1>"
        f'<p class="sub">seed {seed_id} · consensus_mode: {mode}</p>'
        '<p class="legend">Legend: '
        '<span class="stance pos">+</span>adopt/bullish/support '
        '<span class="stance neu">0</span>wait/neutral '
        '<span class="stance neg">−</span>resist/bearish/oppose</p>'
        "<h2>Horizon × intensity</h2>"
        + _grid_html(rows)
        + _distribution_html(rows)
        + '<div class="disclaimer"><b>Scenario rehearsal, not a forecast.</b> '
        "Synthetic personas, not real opinion; not backtested. This report decides no "
        "number, recommends no action, and writes back into no decision.</div>"
        "</body></html>"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a --sweep JSON into a static HTML report.")
    parser.add_argument("--input", default=None, help="sweep JSON file (default: stdin)")
    parser.add_argument("--out", default=None, help="output HTML file (default: stdout)")
    args = parser.parse_args(argv)
    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(rows, list):
        print("error: expected a JSON array (run with --sweep)", file=sys.stderr)
        return 2
    html_out = build_html(rows)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(html_out)
    else:
        print(html_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
