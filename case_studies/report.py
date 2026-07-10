"""Reproduce a case study's key outputs on the command line (part-010).

    PowerShell:  $env:PYTHONPATH="src;$PWD"; python case_studies/report.py A
    bash:        PYTHONPATH="src:$PWD" python case_studies/report.py A

Prints the buckets, per-mode consensus, stance distribution, sweep, and divergence for
one case (A / B / C). Deterministic — same output every run. Rehearsal, not a forecast.
"""

from __future__ import annotations

import sys

from case_studies.cases import CASE_A, CASE_B, CASE_C
from case_studies.runner import run_case

_CASES = {"A": CASE_A, "B": CASE_B, "C": CASE_C}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    key = (args[0].upper() if args else "A")
    spec = _CASES.get(key)
    if spec is None:
        print(f"unknown case {key!r}; choose one of {sorted(_CASES)}", file=sys.stderr)
        return 2
    r = run_case(spec)
    print(f"# {r.label}  (domain: {r.domain})")
    print(f"buckets:            {r.buckets}")
    print(f"consensus by mode:  {r.consensus_by_mode}")
    print(f"stance distribution:{r.stance_distribution}")
    print(f"your posture:       {r.your_posture}  -> divergence: {r.divergence_bucket}")
    print("sweep (horizon x intensity):")
    for h, i, c in r.sweep:
        print(f"  {h:9} {i:6} {c}")
    print("divergence storylines:")
    for s in r.divergence_storylines:
        print(f"  - {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
