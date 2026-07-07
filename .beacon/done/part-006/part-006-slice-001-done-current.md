# DONE — part-006 / slice-001: Optional voice variants (deterministic pick)

Source: BACKLOG backlog-003.

## Goal (achieved)

新增選配 `voice_variants` 表 + engine `_pick_voice`（seed_hash 決定選句），有 variants
的 persona 敘事可多樣、同 seed 決定論；無 variants 的 pack 零漂移。

## What shipped

- `domains/base.py`：`DomainPack` 加 `voice_variants`（預設空 dict）；`validate_pack`
  驗證（persona ∈ roster、每 variant 為非空 str tuple）。
- `engine.py`：`_pick_voice(pack, persona, stance, seed_hash)`——有 variants 則由
  seed_hash 切片 + per-persona offset 選一句，否則 fallback 到單句 `voice`。
  `_excerpt_for`（加 seed_hash 參數）、`_reaction_chain._line`、`EngineFacts.voice_line`
  三處全改用 `_pick_voice`。
- `domains/stock_tw.py`：為 `panic_retail`、`ptt_dcard_trendwatch` 加 3 句/stance 變體示範。
- `tests/`：test_contracts.py +5（variant 驗證）、test_engine.py +4（決定論/跨 seed 多樣/
  變體屬於宣告集/no-variants 回歸）。

## Firewall / determinism

- variants 全為類別字串；validate_pack 拒非字串/空 tuple。
- 選句由 seed_hash 決定（非隨機）→ 同 seed 同句。
- no-variants pack byte-identical（回歸鎖 `test_pack_without_variants_narrative_unchanged`）。

## Verification evidence

- `pytest -q` → **107 passed**（98 + 9）
- `ruff check .` → clean
- Manual QA: panic_retail 在 8 個 rng_seed 下 → 5 種不同敘事；同 seed 決定論一致。

## Incidents

None.
