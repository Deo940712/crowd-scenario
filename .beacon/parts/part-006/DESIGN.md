# part-006 DESIGN

Source: BACKLOG backlog-003 (idea / enhancement)

## Goal

提升敘事多樣性：目前每 persona 每 stance 只有一句固定 voice → 同 stance 組合的敘事
逐字相同。讓每 stance 可有 2-3 句變體，由 seed hash 決定選哪句（仍 byte-stable）；
選配讓反應鏈長度隨 intensity 伸縮。

## Non-goals

- 不破壞決定論（同 seed 必同輸出）。
- 不改 stance / consensus / 防火牆。
- 不引入隨機（變體選擇必須由 seed hash 決定）。

## Assumptions

- `DomainPack.voice: dict[str, dict[int, str]]`——每 persona 每 stance 一句 str。
- `engine.py` 在 `_excerpt_for` 與 `_reaction_chain._line` 取 `pack.voice[id][stance]`。
- seed_hash 是既有決定論來源，可用於選變體。

## Design Options

- **A. voice 值改成 tuple[str, ...] 變體**：`voice[id][stance]` 從 str 變 `tuple[str,...]`，
    engine 用 seed_hash 決定索引。破壞性：所有 pack + validate_pack + 取用點都要改。
- **B. 新增選配的 voice_variants 表（選定）**：保留 `voice`（單句，向後相容），新增
    選配 `voice_variants: dict[str, dict[int, tuple[str, ...]]] = {}`。engine 若某
    persona/stance 有 variants 則由 seed_hash 選一句，否則 fallback 到 `voice`。
    零破壞、漸進、pack 可選擇性提供。
- **C. LLM 生成變體**：違反 zero-dep / 決定論定位（FusionNarrator 已是可選路徑）。捨棄。

## Chosen Design

選 **B**。
- `DomainPack` 加 `voice_variants`（預設空 dict），`validate_pack` 驗證：若提供，keys ⊆
    persona_ids、每項覆蓋的 stance 值為非空 str tuple、每句過防火牆精神（非數字）。
- `engine.py` 加 `_pick_voice(pack, persona, stance, seed_hash) -> str`：有 variants →
    `variants[int(seed_hash[k:k+2],16) % len]`；否則 `pack.voice[persona][stance]`。
- `_excerpt_for` 與 `_reaction_chain._line` 改用 `_pick_voice`。
- 決定論：索引來自 seed_hash（固定），同 seed 同句。
- 反應鏈長度伸縮（選配 slice-002）：severe 時展開 tail 為多步；mild 維持現況。

STOCK_TW 可選擇性為幾個代表 persona 加 2-3 句變體當示範（不必全補）。

## Verification Targets

- Unit：`tests/test_engine.py` + pack 測試。
- 有 variants 的 persona：不同 seed 可選到不同句（多樣性）；同 seed 同句（決定論）。
- 無 variants：行為與現況一致（回歸）。
- 防火牆：所有變體過 `scan_violations`。

## Unit Test Strategy

- `test_voice_variants_are_deterministic_per_seed`：同 seed 兩次同句。
- `test_voice_variants_can_differ_across_seeds`：兩個不同 seed 可選到不同變體
    （對有 variants 的 persona）。
- `test_pack_without_variants_unchanged`：無 variants 的 pack 敘事 byte-identical（回歸）。
- `test_variants_pass_firewall`：每條變體 `scan_violations` 為空。
- `validate_pack` 對壞 variants（空 tuple / 非 str / 未知 persona）報 ContractError。

## Manual QA Strategy

`run --symbol 0056 --seed 1` vs `--seed 2`（不同 seed）→ 對有 variants 的 persona 敘事
可不同；同 seed 兩次相同。

## Risks

- 決定論回歸：無 variants 的既有 pack 不得漂移 → `_pick_voice` 的 no-variants 分支必須
    等價於現況 `pack.voice[id][stance]`。回歸測試 pin。
- 索引偏差：seed_hash 切片選 modulo，需確保決定論且分布合理（非防火牆問題）。

## Open Questions

- variants 索引用 seed_hash 的哪幾個 byte？→ 用固定 offset（如 persona 在 roster 的
    index 決定 offset），確保不同 persona 不會全選同一句。細節由 slice-001 定。
