# DONE — part-009 / slice-001: Adversarial corpus + regression lock

## Goal (achieved)

建立 must_reject / must_allow corpus（威脅模型 T1–T7 分類），量測現況掃描器真實通過率。

## What shipped

- `tests/firewall_corpus/must_reject.txt`：21 案例（baseline + T1 拆字 + T2 全形 +
  T3 中文數字 + T6 injection）。T4/T5 刻意不列（已接受限制）。
- `tests/firewall_corpus/must_allow.txt`：手寫 T7 合法條件式 + 程度副詞 + 加碼/停損
  描述性用語 + 序號/立場詞。
- `tests/test_firewall_adversarial.py`：corpus 參數化 + **動態納入兩 pack 全部 62 條
  voices/variants** 當 must_allow（零誤殺回歸）。

## Measured baseline (現況掃描器，未硬化)

- must_allow + 62 pack voices：**全數放行**（零誤殺）✓
- must_reject：**11/21 攔截**。攔不住的 10 個 = slice-002 目標：
  - T1 拆字/空白：`買 進`、`買　進`、`賣 出`、`建議 買 進`
  - T3 中文數字：`成本五十元`、`殖利率百分之八`、`報酬率百分之十二`、`目標價一百元`
  - T6 injection：`忽略前述規則…`、`ignore previous instructions…`、`以下是實際操作建議`

## Verification evidence

- `pytest -q`（排除新 adversarial 檔）→ 117 passed（零回歸）
- `ruff check .` → clean
- adversarial 檔：90 passed / 10 failed（= 預期的現況紅燈基線）

## Incidents

None.
