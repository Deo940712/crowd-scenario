# Verification Report — part-009

Source: Codex review 短板 #3（regex firewall 需 adversarial tests；宣稱需精確）。

## slice-001: adversarial corpus + regression lock — PASS
## slice-002: scanner hardening (normalize + patterns) — PASS
## slice-003: two-layer security claim in docs — PASS

| Target | Command | Result |
| --- | --- | --- |
| Adversarial corpus | `pytest tests/test_firewall_adversarial.py -q` | 100 passed |
| Full suite | `pytest -q` | 217 passed (117 → 217, +100 corpus cases) |
| Lint | `ruff check .` | All checks passed |
| Corpus coverage | must_reject 21/21 caught; must_allow + 62 voices 0 false-positive | pass |
| Docs encoding | README.md / README.zh-TW.md / firewall.md | no replacement char |

## Threat model outcome

| Threat | Status |
| --- | --- |
| T1 character splitting / spacing | ✅ handled (NFKC + de-space) |
| T2 fullwidth / homoglyph digits | ✅ handled |
| T3 Chinese numerals + unit | ✅ handled (unit-anchored) |
| T6 prompt-injection markers | ✅ handled (heuristic) |
| T7 legitimate conditional prose | ✅ allowed (0 false-positive) |
| T4 semantic advice, no banned word | ❌ documented limitation |
| T5 encoded / obfuscated payload | ❌ documented limitation |

## backlog-006 resolved

「no number leaves / 沒有任何數字」全面改為「no decision-grade additive scalar +
no raw market number」，兩份 README + firewall.md 同步。

New files: `tests/firewall_corpus/{must_reject,must_allow}.txt`,
`tests/test_firewall_adversarial.py`.
Changed: `narrator/firewall.py`, `README.md`, `README.zh-TW.md`, `references/firewall.md`.

---

## PART part-009 — COMPLETE

Firewall security claim upgraded from "rule-based demo" to "adversarially validated,
limitations documented". Structural contract stays the primary guarantee; scanner is
honest defense-in-depth.
- `pytest -q` → 217 passed
- `ruff check .` → clean
