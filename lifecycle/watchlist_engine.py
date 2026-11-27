import pandas as pd
from config.config import LONG_ENTRY, PULLBACK_CONFIG

def build_long_watchlist(stocks, registry=None):
    stocks_clean = stocks.copy()

    # 1. NEW ENTRY (Get-In Criteria)
    allowed_entry_themes = LONG_ENTRY.get("THEMES", ["Leading", "Micro Leader"])
    blocked_zacks = LONG_ENTRY.get("BLOCKED_ZACKS", [])

    min_52w = PULLBACK_CONFIG.get("LONG_MIN_52W_RANGE", 85.0)
    col_52w = "Price as a % of 52 Wk H-L Range"
    range_52w = pd.to_numeric(stocks_clean[col_52w], errors="coerce").fillna(0.0) if col_52w in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    zacks_numeric = pd.to_numeric(stocks_clean["Zacks Rank"], errors="coerce").fillna(0).astype(int) if "Zacks Rank" in stocks_clean.columns else pd.Series(0, index=stocks_clean.index)
    close_numeric = pd.to_numeric(stocks_clean["Last Close"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Last Close" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    vol_numeric = pd.to_numeric(stocks_clean["Avg Volume"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Avg Volume" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    dollar_vol = close_numeric * vol_numeric
    growth_score = stocks_clean["Growth Score"].astype(str).str.strip().str.upper() if "Growth Score" in stocks_clean.columns else pd.Series("", index=stocks_clean.index)

    # 1. STATELESS DAILY EVALUATION (Unified Long Screening)
    min_rs = LONG_ENTRY.get("MIN_RS", 0.0)
    min_pct_off_low = LONG_ENTRY.get("MIN_PCT_OFF_LOW", 0.0)
    min_52w = PULLBACK_CONFIG.get("LONG_MIN_52W_RANGE", 0.0)
    breakout_rs = LONG_ENTRY.get("BREAKOUT_MIN_RS", 90.0)
    breakout_range = PULLBACK_CONFIG.get("LONG_BREAKOUT_MIN_52W_RANGE", 85.0)
    allowed_zacks = LONG_ENTRY.get("ALLOWED_ZACKS", [1, 2])

    if "52 Week Low" in stocks_clean.columns and "Last Close" in stocks_clean.columns:
        low_clean = pd.to_numeric(stocks_clean["52 Week Low"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").replace(0, float('nan'))
        pct_off_low = ((close_numeric - low_clean) / low_clean * 100.0).fillna(0.0)
    else:
        # Fallback for historical files missing raw 52 Week Low
        pct_off_low = range_52w.fillna(0.0)

    stocks_clean["% off Lo"] = pct_off_low

    # Sector Filter: Never swim upstream against lagging sectors
    blocked_sector_statuses = LONG_ENTRY.get("BLOCKED_SECTOR_STATUSES", ["LAGGING"])
    sector_ok = (
        ~stocks_clean["Sector_Status"].isin(blocked_sector_statuses)
        if "Sector_Status" in stocks_clean.columns
        else pd.Series(True, index=stocks_clean.index)
    )

    # Standard Entry: Leading theme + Non-lagging sector + Zacks 1-2 + Price >= $10 + Vol >= 1M
    standard_entry_mask = (
        stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & sector_ok
        & (stocks_clean["RS_Rating"] >= min_rs)
        & (zacks_numeric.isin(allowed_zacks))
        & (pct_off_low >= min_pct_off_low)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (
            (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
            | ((vol_numeric >= LONG_ENTRY.get("ELITE_ALT_MIN_VOLUME", 500_000)) & (dollar_vol >= LONG_ENTRY.get("ELITE_ALT_MIN_DOLLAR_VOL", 30_000_000)))
        )
    )

    # Zacks 3 Exception: Leading theme + Exceptional RS >= 95 + Growth A/B/C
    z3_exception_enabled = LONG_ENTRY.get("ZACKS_3_EXCEPTION_ENABLED", False)
    z3_min_rs = LONG_ENTRY.get("ZACKS_3_ALLOWED_MIN_RS", 95.0)
    z3_growth = LONG_ENTRY.get("ZACKS_3_ALLOWED_GROWTH", ["A", "B", "C"])
    z3_exception_mask = pd.Series(False, index=stocks_clean.index)
    if z3_exception_enabled:
        z3_exception_mask = (
            stocks_clean["Theme_Class"].isin(allowed_entry_themes)
            & (stocks_clean["RS_Rating"] >= z3_min_rs)
            & (zacks_numeric == 3)
            & (growth_score.isin(z3_growth))
            & (range_52w >= min_52w)
            & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
            & (
                (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
                | ((vol_numeric >= LONG_ENTRY.get("ELITE_ALT_MIN_VOLUME", 500_000)) & (dollar_vol >= LONG_ENTRY.get("ELITE_ALT_MIN_DOLLAR_VOL", 30_000_000)))
            )
        )

    stocks_clean["Is_Elite_Exception"] = False
    new_elite_mask = z3_exception_mask & (~standard_entry_mask)
    if new_elite_mask.any():
        stocks_clean.loc[new_elite_mask, "Is_Elite_Exception"] = True

    # Independent Leader Theme Exemption (Safety Valve against flawed/neutral themes):
    # Exceptional RS (>= 95.0), Range >= 85%, Zacks 1-2
    theme_exemption_enabled = LONG_ENTRY.get("THEME_EXEMPTION_ENABLED", True)
    theme_exempt_min_rs = LONG_ENTRY.get("THEME_EXEMPTION_MIN_RS", 95.0)
    theme_exempt_min_range = LONG_ENTRY.get("THEME_EXEMPTION_MIN_RANGE", 85.0)
    theme_exempt_zacks = LONG_ENTRY.get("THEME_EXEMPTION_ALLOWED_ZACKS", [1, 2])

    theme_exempt_mask = pd.Series(False, index=stocks_clean.index)
    if theme_exemption_enabled:
        theme_exempt_mask = (
            (stocks_clean["RS_Rating"] >= theme_exempt_min_rs)
            & (range_52w >= theme_exempt_min_range)
            & (zacks_numeric.isin(theme_exempt_zacks))
            & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
            & (
                (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
                | ((vol_numeric >= LONG_ENTRY.get("ELITE_ALT_MIN_VOLUME", 500_000)) & (dollar_vol >= LONG_ENTRY.get("ELITE_ALT_MIN_DOLLAR_VOL", 30_000_000)))
            )
        )

    stocks_clean["Is_Theme_Exempt"] = False
    new_exempt_mask = theme_exempt_mask & (~standard_entry_mask) & (~z3_exception_mask)
    if new_exempt_mask.any():
        stocks_clean.loc[new_exempt_mask, "Is_Theme_Exempt"] = True

    qualifying_mask = standard_entry_mask | z3_exception_mask | theme_exempt_mask

    # Tag setup type: Breakout vs Pullback
    is_breakout = (stocks_clean["RS_Rating"] >= breakout_rs) & (range_52w >= breakout_range)
    stocks_clean["Setup_Type"] = is_breakout.map({True: "Breakout", False: "Pullback"})

    long_watchlist = stocks_clean[qualifying_mask].copy()
    
    if long_watchlist.empty:
        return long_watchlist
        
    long_watchlist = long_watchlist.sort_values(
        ["RS_Rating"],
        ascending=[False]
    )

    # Deduplicate to prevent a duplicate stock from appearing multiple times
    long_watchlist = long_watchlist.drop_duplicates(subset=["Ticker"])
    
    # Re-sort natively post-grouping to ensure it drops into presentation smoothly
    long_watchlist = long_watchlist.sort_values(
        ["RS_Rating"],
        ascending=[False]
    )


    return long_watchlist
