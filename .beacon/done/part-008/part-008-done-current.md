# DONE — part-008: Consensus model evaluation (4 slices)

Source: Codex review + internal review（hashed default 反直覺；current aggregate 仍受
hashed baseline 影響）。**不預設結論**，用實驗矩陣選擇。

## slice-001: Lock current consensus models — DONE

- `tests/test_engine.py`：`_EVAL_CASES`（5 案例，**實測值** pin hashed+aggregate golden）、
  `test_current_modes_pinned_for_evaluation_corpus`、`test_default_is_hashed_pinned`。
- 明示 CURRENT public default == hashed（未改）。

## slice-002: Experimental neutral-baseline aggregate — DONE

- `engine.py`：`CONSENSUS_MODES` 加 `aggregate_neutral`；persona baseline 用 `neutral`
  → 方向純由 ordinal context 決定，**不受 seed hash 影響**。hashed/aggregate byte-stable。
- `cli.py`：`--consensus-mode` 加 `aggregate_neutral`（help 標 EXPERIMENTAL）。
- `tests/`：決定論、hash-independence、中性穩定、net-sign 規則（6 測試）。

## slice-003: Comparison matrix — DONE

- `tools/eval_consensus.py`：固定 case corpus（兩 pack × 正/負/中）→ 三模型對照 +
  counter-intuitive/majority-disagree/hash-independence 統計 → Markdown。決定性。
- `tests/test_consensus_eval.py`：可重現 + net-sign 一致（3 測試）。

## slice-004: Default recommendation — DONE (design-only)

- `.beacon/done/part-008/consensus-evaluation.md`：矩陣 + 五準則逐條決策。

## Key result

| metric | hashed | aggregate | aggregate_neutral |
| --- | --- | --- | --- |
| counter-intuitive rows | 2 | 1 | **0** |
| disagrees w/ persona majority | 1 | 1 | **0** |
| hash-independence | n/a | ✗ | **✓** |

**Recommendation: adopt `aggregate_neutral` as the public default** — most explainable,
most semantically consistent, hash-independent. Execution deferred to **part-013**
(evidence-gated), whose gate is now satisfied by the evaluation report.

Also decided: **backlog-007 (pack prior) not needed** — neutral baseline did not
over-neutralize.

## Verification evidence

- `pytest -q` → **232 passed**（223 → 232，+9 across slices; zero regression on
  hashed/aggregate golden）
- `ruff check .` → clean
- `python tools/eval_consensus.py` → reproducible matrix; hash-independence True

## Incidents

None. (Note: slice-001 golden values were MEASURED from the engine, not guessed — an
early draft with guessed values was corrected against real output, avoiding a
"fit the test to the answer" hack.)
