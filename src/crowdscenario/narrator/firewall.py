"""The rule-based firewall scanner — the single gate every LLM output must pass.

``DeterministicNarrator`` prose is scalar-free by construction. ``FusionNarrator``
prose comes from LLMs, which can hallucinate a price, a percentage, or an absolute
buy/sell order. This scanner is the deterministic, offline check that screens EVERY
LLM output (both writers AND the judge) before any of it is allowed into a
``CrowdNarrative``. Non-empty result → that candidate is rejected.

It enforces, at the text layer, the same red-lines the contract enforces at the type
layer (see ``references/firewall.md`` and ``agent/SOUL.md`` rules 6/9/10):

- No numeric market token: a bare number attached to a price/NAV/currency/percent/
  yield context. (Structural digit-context patterns, not "the engine emitted a float".)
- No absolute buy/sell / order language: 買進/賣出/加碼/減碼/停損/委託單/掛單 and the
  English "buy it / sell it / place an order" family.

This is intentionally conservative: it would rather reject a clean-but-suspicious line
than let a leak through, because the fallback (deterministic prose) is always safe.
"""

from __future__ import annotations

import re

# Digits in ANY width: LLM zh-TW prose routinely emits fullwidth digits (０-９) and a
# fullwidth percent (％), which ASCII-only patterns miss entirely. This class is reused
# everywhere a "digit" is matched below so a fullwidth number cannot slip a metric past.
_D = r"[0-9\uFF10-\uFF19]"

# --- Numeric market tokens ---------------------------------------------------------
# A digit that sits in a price / currency / percent / NAV / yield context. We do NOT
# flag ordinal list markers ("1. ", "2. ") or the stance labels; those carry no metric.
_NUMERIC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("currency_ntd", re.compile(rf"(?:NT\$|NTD|新台幣|台幣|元|塊)\s*{_D}", re.IGNORECASE)),
    ("currency_trailing", re.compile(rf"{_D}[\d,.\uFF10-\uFF19]*\s*(?:元|塊|億|萬)")),
    ("percent", re.compile(rf"{_D}[\d,.\uFF10-\uFF19]*\s*[%\uFF05]|百分之\s*{_D}")),
    (
        "price_nav",
        re.compile(rf"(?:股價|淨值|NAV|報價|價格|市價|目標價)\s*[:：]?\s*{_D}", re.IGNORECASE),
    ),
    ("yield_num", re.compile(rf"(?:殖利率|配息率|報酬率|漲跌幅)\s*[:：]?\s*{_D}")),
    ("bare_decimal", re.compile(r"(?<![\d\uFF10-\uFF19])\d+\.\d+")),
    # Internal numeric signal encodings a leaked prompt could carry. stance/score/
    # modifier/weight are engine-internal ordinals that must never surface in prose.
    ("signal_token", re.compile(r"\b(?:stance|score|modifier|weight)\s*=", re.IGNORECASE)),
)

# --- Absolute buy/sell / order language --------------------------------------------
# Conditional persona wording ("這類人格可能傾向…") is fine; an imperative order is not.
# Bare 買進/賣出 are included so the scanner matches what README documents ("order
# phrase (買進/賣出/委託單 …) is rejected"). The deterministic persona voices only ever
# use them in compounds like 加碼/停損/出貨 (conditional description, kept), never as a
# flat 買進/賣出 imperative — that flat form is exactly the order we must drop.
_ORDER_TERMS: tuple[str, ...] = (
    "買進",
    "賣出",
    "委託單",
    "掛單",
    "下單",
    "掛買",
    "掛賣",
    "停損單",
    "市價單",
    "限價單",
    "務必買進",
    "務必賣出",
    "建議買進",
    "建議賣出",
    "應該買進",
    "應該賣出",
    "快買",
    "快賣",
    "全力買進",
    "全數賣出",
    "現在就買",
    "現在就賣",
)
_ORDER_EN = re.compile(
    r"\b(?:place\s+(?:an?\s+)?order|buy\s+it\s+now|sell\s+it\s+now|you\s+should\s+(?:buy|sell))\b",
    re.IGNORECASE,
)


def scan_violations(text: str) -> tuple[str, ...]:
    """Return a tuple of violation tags found in ``text``. Empty tuple == clean.

    Deterministic and offline. A non-empty result means the candidate MUST be
    rejected before it can enter a CrowdNarrative.
    """
    hits: list[str] = []
    for tag, pattern in _NUMERIC_PATTERNS:
        if pattern.search(text):
            hits.append(f"numeric:{tag}")
    for term in _ORDER_TERMS:
        if term in text:
            hits.append(f"order:{term}")
    if _ORDER_EN.search(text):
        hits.append("order:en")
    return tuple(hits)


def is_clean(text: str) -> bool:
    """True if ``text`` carries no firewall violation."""
    return not scan_violations(text)
