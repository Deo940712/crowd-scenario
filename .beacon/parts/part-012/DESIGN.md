# part-012 DESIGN

Source: Codex review「更多 domain pack」+ 內部評估：第三個 domain 不應只是換皮，
要證明引擎不是「換名稱的股票 sentiment 模型」。選定 **software migration /
breaking-change rollout**——非金融、非消費發表，但天然有群眾動力學。

## Goal

新增 `SOFTWARE_MIGRATION` DomainPack：排練「一個重大版本 / breaking change 公告後，
軟體生態系的各方會怎麼反應」。證明 DomainPack 協議承載得了與金融完全不同的語義。

## Non-goals

- 不改引擎 core（若 pack 塞不進現有協議，那是重要發現 → 開 incident/新 PART，不硬改）。
- 不做真實 GitHub 資料串接（輸入仍是手工 bucketed 快照）。
- 不宣稱能預測任何真實專案的遷移結果。

## Assumptions

- `DomainPack` 協議已被兩個 pack 驗證（persona/axes/voice/sensitivity/consensus_display/
  horizon_frame/voice_variants）。
- `validate_pack` 會擋掉不完整的 pack（voice 覆蓋、平行表對齊等）。
- consensus 中性詞彙 `negative|neutral|positive` 映射為本 domain 的
  `resist（抵制）| wait（觀望）| adopt（採用）`。

## Pack 草案

**personas（8 個，roster 序 = 反應鏈 tie-break 序）**：

| id | 顯示名 | herding | 傾向 |
|---|---|---|---|
| early_adopter | 嘗鮮開發者 | 0.85 | 高敏感、正向偏好新功能 |
| oss_maintainer | 下游套件維護者 | 0.30 | 對 breaking 幅度極敏感（contra 傾向）|
| enterprise_ops | 企業運維 | 0.15 | 最慢、對遷移成本極敏感 |
| plugin_ecosystem | 外掛生態作者 | 0.45 | 對 API 穩定性敏感 |
| security_team | 資安團隊 | 0.25 | 對 EOL/支援期敏感、方向常與潮流無關 |
| hobby_user | 業餘使用者 | 0.70 | 跟風、對文件品質敏感 |
| tech_influencer | 技術 KOL / 社群風向 | 0.95 | 最快、放大情緒 |
| conservative_team | 保守團隊（LTS 派）| 0.20 | contra：潮流越熱越觀望 |

**axes（3 條，序數桶示意）**：

1. `breaking_severity`（破壞幅度）：`cosmetic / minor / major / rewrite`
   → tilt：越大越負。
2. `migration_effort`（遷移成本，含工具輔助度）：`automated / guided / manual / painful`
   → tilt：越痛越負。
3. `value_gain`（新版帶來的感知價值）：`negligible / modest / substantial / game_changing`
   → tilt：越大越正。

**consensus_display**：`negative→resist`、`neutral→wait`、`positive→adopt`。

**horizon_frame**：`intraday→公告當週`、`swing→一個發佈週期`、`long→LTS 週期`。

（persona 語音 zh-TW，各 stance 一句 + 為 tech_influencer / hobby_user 加 variants 示範。）

## Design Options

- **A. 最小 pack（無 variants、平均 sensitivity）**：能跑但示範性弱。捨棄。
- **B. 完整 pack + case（選定）**：完整 sensitivity 差異化 + 2 個 persona variants +
    一個 fixture 情境（如「Python 2→3 型 rewrite」與「工具完備的 major 升級」對照），
    並直接掛進 CLI `_DOMAINS`/`_FIXTURES`。
- **C. pack + 引擎擴充（如 persona 間影響網路）**：超出本 PART，留給未來。捨棄。

## Chosen Design

選 **B**。檔案：`src/crowdscenario/domains/software.py`（`SOFTWARE_MIGRATION`），
輸出加進 `domains/__init__.py` 與頂層 `__init__.py`；CLI `_DOMAINS` 註冊
`software_migration`；`_FIXTURES` 加 2–3 個示範情境；README 兩份的 domain 清單更新。

語義自檢（pack 設計正確性的驗收直覺）：
- 「rewrite 級破壞 + painful 遷移 + negligible 價值」→ aggregate 應 resist。
- 「minor 破壞 + automated 遷移 + substantial 價值」→ aggregate 應 adopt。
- enterprise_ops / conservative_team 在任何熱潮下都慢半拍（herding 低 + contra）。

## Verification Targets

- `validate_pack` 通過（建構即驗證）。
- 既有 pack-agnostic 參數化測試（`_PACKS`）擴充納入第三 pack 全綠。
- 語義自檢兩情境的 aggregate 方向正確（新測試）。
- CLI：`run --domain software_migration --symbol big_rewrite ...` 可跑。
- `pytest -q` 全綠、`ruff` clean。

## Unit Test Strategy

- 把 `SOFTWARE_MIGRATION` 加進 test_engine 的 `_PACKS` 參數化（自動獲得決定論/
  categorical/no-leak/roster 全套覆蓋）。
- `test_software_pack_semantic_sanity`：兩個語義自檢情境。
- `test_software_pack_display_vocabulary`：resist/wait/adopt 映射正確。

## Manual QA Strategy

- CLI 跑 2 個 fixture 情境 + sweep，肉眼確認敘事通順、persona 分歧合理。
- （若 part-011 已完成）產一份 HTML 報告目視。

## Risks

- persona 語音寫成金融腔 → 語音全部重寫為軟體生態語境，抽查過 scan_violations
  （注意：`買進/賣出` 掃描規則不影響本 domain，但「立刻升級」類指令語氣要留意——
  掃描器目前只攔市場下單語，本 domain 的「快升級」不是市場指令，屬合法條件敘事）。
- 3 條軸 × 8 personas 的 sensitivity 表手工調參易失衡 → 用語義自檢測試鎖方向，
  不追求精確數值。
- roster 8 人與 STOCK_TW 10 人不同 → 引擎已 pack-agnostic（PRODUCT_LAUNCH 也是 8），無風險。

## Open Questions

- fixture 情境名用抽象（big_rewrite / smooth_major）或影射真實案例（py2to3）？
  → 傾向抽象名 + 文件註明「原型參考」，避免對真實專案下判斷的觀感。slice 定案。
