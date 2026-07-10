# DONE — part-009 / slice-002: Scanner hardening (normalize + patterns)

## Goal (achieved)

修可修的威脅類別，讓 must_reject corpus 全綠、must_allow（含 62 pack voices）零誤殺。

## What shipped

- `firewall.py`：
  - **正規化層**：`_normalize()` = NFKC fold + 去零寬字元（ZWSP/ZWNJ/ZWJ/BOM/soft-hyphen）
    + 去分隔字元（空白、`·‧・._．・` 全形點）。`scan_violations` 掃兩份副本：
    `folded`（NFKC，保留空白/點）給 numeric patterns；`collapsed`（去分隔）給
    order-term / injection 字面匹配。**呼叫者的原始文字永不被改動。**
  - **T3 中文數字**：`cn_numeral_unit`（`[一二三四…百千萬兩○零]+ + 元/塊/億/％/%`）、
    `cn_percent`（`百分之 + 中文數字`）。**帶單位錨點**，故「十分看好/三分鐘/萬一」不誤殺。
  - **T6 injection**：`_INJECTION` 中英標記詞（忽略前述、以下是實際操作建議、
    ignore previous instructions、here's the real advice…），folded+collapsed 雙掃。

## Result — corpus 從 11/21 → 21/21 攔截

修好的類別：
- T1 拆字/空白：`買 進`、`買　進`、全形 `Ｂ Ｕ Ｙ` → collapsed 後匹配 ✓
- T2 全形數字/字母：NFKC fold ✓（原本已部分覆蓋，現更穩）
- T3 中文數字：`成本五十元`、`百分之八`、`目標價一百元` ✓
- T6 injection：中英標記詞 ✓

零誤殺驗證（should ALLOW，全部放行）：
- 程度副詞：`十分看好`、`三分鐘熱度`、`萬一` ✓
- 描述性複合詞：`越跌越買`、`調節持股`、`快速停損出場` ✓
- 62 條 pack voices/variants ✓

## Verification evidence

- `pytest tests/test_firewall_adversarial.py -q` → **100 passed**（must_reject 全攔 +
  must_allow 全放 + 62 voices 零誤殺）
- `pytest -q` → **217 passed**（原 117 + 100 corpus 案例，零回歸；含
  `test_deterministic_narrative_is_clean`）
- `ruff check .` → clean

## Known limitations (carried to slice-003 docs)

- T4（語義型建議，無禁詞，如「現在是很適合採取行動的時候」）：規則式無法辨識。
- T5（編碼/暗號，Base64/諧音）：規則式無法辨識。
兩者是**已接受的限制**，將於 slice-003 誠實文件化。

## Incidents

None.
