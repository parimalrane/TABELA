"""
Dynamic Micro-Leader / Micro-Lagging Engine
===========================================

Problem solved: a micro theme (e.g. Cybersecurity) can be strongly diverging from
its parent macro theme (e.g. Software, ranked Neutral/Lagging), yet its stocks are
locked out of the watchlists because every stock inherits its parent's class.

Rule (fully dynamic, no ticker hard-coding):

  MICRO LEADER   (parent is NOT Leading)
      Pillar 1  sub-ETF(s) of the micro theme beat the benchmark  (ETF_RS > 0)
                -> only evaluated if the micro theme has its own ETF row;
                   otherwise Pillar 1 is skipped (breadth-only).
      Pillar 2  ungated weighted breadth  W_Brdth >= MIN_W_BREADTH
      -> stocks promoted to Theme_Class = "Leading"   (Micro_Tier = "Micro Leader")

  MICRO LAGGING  (parent is NOT Lagging)  -- exact mirror
      Pillar 1  sub-ETF(s) trail the benchmark (ETF_RS < 0)
      Pillar 2  ungated bearish weighted breadth >= MIN_W_BREADTH
      -> stocks promoted to Theme_Class = "Lagging"   (Micro_Tier = "Micro Lagging")

Design notes
  * config/config.py is NOT touched. Promoted stocks reuse the existing
    Leading/Lagging classes so every existing gate (RS, Zacks, 52W range,
    volume, TABELA retention) still applies unchanged. Only the *theme gate*
    is unlocked.
  * Micro_Tier / Micro_ETF / Micro_ETF_RS columns carry the label for reporting.
  * Fail-safe: any error or missing data returns the stocks unchanged.
"""

import math
import re
from pathlib import Path

import pandas as pd

MICRO_THEME_CONFIG = {
    "ENABLED": True,
    # Weighted-breadth threshold (same formula as scoring/breadth_engine.py)
    "MIN_W_BREADTH": 40.0,
    # Themes with NO dedicated ETF have no Pillar-1 confirmation, so they must
    # prove themselves with a stronger breadth reading (multiplier on MIN_W_BREADTH).
    "NO_ETF_BREADTH_MULTIPLIER": 2.0,
    # Sub-ETF relative strength vs benchmark
    "MIN_ETF_RS_LEADER": 0.0,    # must be strictly greater
    "MAX_ETF_RS_LAGGARD": 0.0,   # must be strictly lower
    # Participation bars used ONLY for theme-level breadth (stock entry gates are unchanged).
    # Bullish: RS_Rating >= LONG_STAY.MIN_RS (75, "Stay-In" level, top ~25% of market).
    # Bearish mirror: Short_RS_Rating <= 100 - 75 = 25 (bottom ~25% of market).
    "BULL_PARTICIPATION_RS": 75.0,
    "BEAR_PARTICIPATION_MAX_SHORT_RS": 25.0,
}


def _parse_etf_tokens(raw):
    """'[XLK] CIBR, BUG' -> ['CIBR', 'BUG']"""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    cleaned = re.sub(r"\[.*?\]", "", str(raw)).strip()
    tokens = []
    for tok in cleaned.split(","):
        tok = tok.strip().split(" ")[0].replace("/", "").upper()
        if tok and tok.isalpha():
            tokens.append(tok)
    return tokens


def _num(val):
    s = str(val).replace("%", "").replace("$", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    return pd.to_numeric(s, errors="coerce")


def _etf_relative_scores(etf_master, benchmark_returns, period_weights):
    """Per-ETF relative score vs benchmark (same weighting as theme strength)."""
    scores = {}
    aum = {}
    for _, row in etf_master.iterrows():
        tkr = str(row.get("Ticker", "")).strip().upper()
        if not tkr:
            continue
        wsum, wtot = 0.0, 0.0
        for period, weight in period_weights.items():
            if not weight:
                continue
            ret = _num(row.get(period))
            bench = benchmark_returns.get(period)
            if pd.isna(ret) or bench is None or pd.isna(bench):
                continue
            wsum += (ret - bench) * weight
            wtot += weight
        if wtot > 0:
            scores[tkr] = wsum / wtot
            a = pd.to_numeric(row.get("Market Value (mil)"), errors="coerce")
            aum[tkr] = float(a) if pd.notna(a) and a > 0 else 0.0
    return scores, aum


def _micro_etf_rs(micro_theme, etf_mapping, scores, aum):
    """AUM-weighted relative score of the micro theme's OWN ETFs (None if none)."""
    raw = etf_mapping.get(micro_theme)
    tokens = [t for t in _parse_etf_tokens(raw) if t in scores]
    if not tokens:
        return None, ""
    total_aum = sum(aum.get(t, 0.0) for t in tokens)
    if total_aum > 0:
        rs = sum(scores[t] * aum.get(t, 0.0) for t in tokens) / total_aum
    else:
        rs = sum(scores[t] for t in tokens) / len(tokens)
    return rs, tokens[0]


def _weighted_breadth(n_total, strengths):
    """Same math as breadth_engine: pct * (avgRS/100) * ln(total+1)."""
    n_strong = len(strengths)
    if n_total <= 0 or n_strong == 0:
        return 0.0, 0
    pct = round(n_strong / n_total * 100, 2)
    avg = float(sum(strengths) / n_strong)
    return round(pct * (avg / 100.0) * math.log(n_total + 1), 2), n_strong


def _load_override_tickers():
    base_dir = Path(__file__).resolve().parent.parent
    f = base_dir / "data" / "unclassified_overrides.csv"
    if not f.exists():
        return set()
    try:
        df = pd.read_csv(f)
        return {str(t).strip().upper() for t in df["Ticker"]}
    except Exception:
        return set()


def apply_micro_theme_promotion(stocks, etf_master, benchmark_returns,
                                theme_strength_settings, theme_class_map,
                                avg_leading_score=80.0):
    """
    Returns (stocks, micro_info).  micro_info: {micro_theme: dict(tier, etf, etf_rs, wb, ...)}
    Always adds Micro_Tier / Micro_ETF / Micro_ETF_RS columns (empty when not promoted).
    """
    stocks = stocks.copy()
    stocks["Micro_Tier"] = ""
    stocks["Micro_ETF"] = ""
    stocks["Micro_ETF_RS"] = pd.NA
    micro_info = {}

    if not MICRO_THEME_CONFIG.get("ENABLED", True):
        return stocks, micro_info

    try:
        from config.config import LONG_ENTRY, SHORT_ENTRY
        from themes.theme_translation_engine import THEME_TRANSLATION, THEME_ETF_MAPPING

        min_wb = MICRO_THEME_CONFIG["MIN_W_BREADTH"]
        long_rs_min = MICRO_THEME_CONFIG["BULL_PARTICIPATION_RS"]
        short_lo = SHORT_ENTRY.get("MIN_SHORT_RS", 8.0)
        short_hi = MICRO_THEME_CONFIG["BEAR_PARTICIPATION_MAX_SHORT_RS"]

        if "Short_RS_Rating" not in stocks.columns or "RS_Rating" not in stocks.columns:
            return stocks, micro_info

        period_weights = theme_strength_settings["period_weights"]
        scores, aum = _etf_relative_scores(etf_master, benchmark_returns, period_weights)

        rs = pd.to_numeric(stocks["RS_Rating"], errors="coerce")
        srs = pd.to_numeric(stocks["Short_RS_Rating"], errors="coerce")
        overrides = _load_override_tickers()
        tickers_clean = stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper()

        for micro, idx in stocks.groupby("Mapped_Theme").groups.items():
            micro = str(micro)
            parent = THEME_TRANSLATION.get(micro, micro)
            if micro == parent:
                continue  # theme IS the macro theme: no divergence to detect

            parent_cls = theme_class_map.get(parent)
            if parent_cls is None:
                continue

            n_total = len(idx)
            etf_rs, etf_tkr = _micro_etf_rs(micro, THEME_ETF_MAPPING, scores, aum)

            tier = None
            wb_val, n_qual = 0.0, 0

            if parent_cls != "Leading":
                m = rs.loc[idx] >= long_rs_min
                wb_val, n_qual = _weighted_breadth(n_total, rs.loc[idx][m].tolist())
                etf_ok = (etf_rs is None) or (etf_rs > MICRO_THEME_CONFIG["MIN_ETF_RS_LEADER"])
                need = min_wb if etf_rs is not None else min_wb * MICRO_THEME_CONFIG["NO_ETF_BREADTH_MULTIPLIER"]
                if etf_ok and wb_val >= need:
                    tier = "Micro Leader"

            if tier is None and parent_cls != "Lagging":
                m = (srs.loc[idx] >= short_lo) & (srs.loc[idx] <= short_hi)
                wb_s, n_q_s = _weighted_breadth(
                    n_total, (100.0 - srs.loc[idx][m]).tolist())
                etf_ok = (etf_rs is None) or (etf_rs < MICRO_THEME_CONFIG["MAX_ETF_RS_LAGGARD"])
                need = min_wb if etf_rs is not None else min_wb * MICRO_THEME_CONFIG["NO_ETF_BREADTH_MULTIPLIER"]
                if etf_ok and wb_s >= need:
                    tier = "Micro Lagging"
                    wb_val, n_qual = wb_s, n_q_s

            if tier is None:
                continue

            target_cls = "Leading" if tier == "Micro Leader" else "Lagging"
            skip_cls = target_cls
            sel = stocks.index.isin(idx) & (stocks["Theme_Class"] != skip_cls)
            # never override explicit whitelist leaders when demoting to Lagging
            if tier == "Micro Lagging":
                sel &= ~tickers_clean.isin(overrides)
            if not sel.any():
                continue

            stocks.loc[sel, "Theme_Class"] = target_cls
            stocks.loc[sel, "Theme_State"] = target_cls
            stocks.loc[sel, "Theme_Score"] = avg_leading_score
            stocks.loc[sel, "Micro_Tier"] = tier
            stocks.loc[sel, "Micro_ETF"] = etf_tkr
            if etf_rs is not None:
                stocks.loc[sel, "Micro_ETF_RS"] = round(float(etf_rs), 2)

            micro_info[micro] = {
                "tier": tier, "etf": etf_tkr, "etf_rs": etf_rs,
                "w_breadth": wb_val, "qual": n_qual, "parent": parent,
                "parent_class": parent_cls, "promoted": int(sel.sum()),
            }

        return stocks, micro_info

    except Exception as exc:  # fail-safe: never break the pipeline
        print(f"WARNING: micro-theme engine skipped ({exc})")
        return stocks, {}
