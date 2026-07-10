# part-012 TODO

Design authority: `.beacon/parts/part-012/DESIGN.md`

## SLICE Map

### part-012-slice-001: SOFTWARE_MIGRATION pack + semantic sanity tests

Status: done — see `.beacon/done/part-012/`

Goal:
建 `SOFTWARE_MIGRATION` DomainPack（8 personas × 3 axes，完整 voice + 2 persona
variants），通過 validate_pack 與語義自檢。

Candidate scope:
- [ ] `src/crowdscenario/domains/software.py`：personas/herding/contra/voice/
      display_name/axes(bucket_fn+tilt)/sensitivity/consensus_display(resist-wait-adopt)/
      horizon_frame/voice_variants（tech_influencer + hobby_user）。
- [ ] `domains/__init__.py` + 頂層 `__init__.py` 匯出。
- [ ] `tests/test_engine.py`：`_PACKS` 加第三 pack；`test_software_pack_semantic_sanity`
      （rewrite+painful+negligible → resist；minor+automated+substantial → adopt）；
      display vocabulary 測試。

Forbidden scope:
- 改引擎 core / DomainPack 協議。
- 影射真實專案的判斷性內容。

Verification target:
- Unit: `pytest tests/test_engine.py tests/test_contracts.py -q`
- Regression: `pytest -q` 全綠、`ruff` clean

Done gate:
- 第三 pack 通過全部 pack-agnostic 測試 + 語義自檢方向正確。

### part-012-slice-002: CLI + docs wiring

Status: done — see `.beacon/done/part-012/`

Goal:
把新 pack 接進 CLI 與文件，使用者可直接體驗第三 domain。

Candidate scope:
- [ ] `cli.py`：`_DOMAINS` 註冊 `software_migration`；`_FIXTURES` 加 2–3 情境；
      `_FALLBACK` 加中性值。
- [ ] `tests/test_cli.py`：新 domain 冒煙（run + sweep）。
- [ ] README.md / README.zh-TW.md：domain 清單加第三 pack + 一個 CLI 範例。

Forbidden scope:
- 同 slice-001。

Verification target:
- Unit: CLI 測試綠
- Manual QA: `run --domain software_migration --symbol big_rewrite --scenario v9_rewrite`
  + `--sweep` 目視

Done gate:
- CLI 三個 domain 可選；文件同步；`pytest`/`ruff` 綠。

Dependencies: slice-002 依賴 slice-001。
