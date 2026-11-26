"""
Bottom-Up & Composite Theme Engine
Calculates institutional theme leadership using a dual-engine architecture:
  1. Top-Down Macro Score: ETF relative momentum (1W, 1M, 3M vs SPY)
  2. Bottom-Up Breadth Score: Constituent stock participation (% near 52W Highs with RS >= 75)
Blends both into a unified Composite Theme Score to classify Leading (30%), Neutral (40%), Lagging (30%).
"""

import pandas as pd
import numpy as np
from config.config import BOTTOM_UP_THEME_CONFIG
from themes.theme_translation_engine import THEME_TRANSLATION


def calculate_bottom_up_theme_classification(stocks, top_down_theme_strength=None, config=None):
    """
    Ranks themes using dual-engine composite scoring:
      - Top-Down ETF momentum (WEIGHT_TOP_DOWN_ETF, default 50%)
      - Bottom-Up stock breadth with Bayesian shrinkage (WEIGHT_BOTTOM_UP_BREADTH, default 50%)
      
    Classification:
      Top TOP_TIER_PCT (default 30%) = Leading
      Bottom BOTTOM_TIER_PCT (default 30%) = Lagging
      Middle (default 40%) = Neutral
    """
    if config is None:
        config = BOTTOM_UP_THEME_CONFIG

    enabled = config.get("ENABLED", True)
    min_rs = float(config.get("LEADER_MIN_RS", 75.0))
    max_off_hi = float(config.get("LEADER_MAX_OFF_HIGH_PCT", 15.0))
    C = float(config.get("SHRINKAGE_C", 10.0))
    top_pct = float(config.get("TOP_TIER_PCT", 0.30))
    bot_pct = float(config.get("BOTTOM_TIER_PCT", 0.30))
    w_td = float(config.get("WEIGHT_TOP_DOWN_ETF", 0.50))
    w_bu = float(config.get("WEIGHT_BOTTOM_UP_BREADTH", 0.50))

    df = stocks.copy()

    # Clean price columns to calculate % off 52-week high
    clean_close = pd.to_numeric(
        df["Last Close"].astype(str).str.replace(r"[%$,]", "", regex=True),
        errors="coerce"
    )
    clean_high = pd.to_numeric(
        df["52 Week High"].astype(str).str.replace(r"[%$,]", "", regex=True),
        errors="coerce"
    )
    
    pct_off_hi = ((clean_high - clean_close) / clean_high * 100.0).fillna(999.0)

    # Individual constituent leadership condition
    rs_col = pd.to_numeric(df.get("RS_Rating", 0), errors="coerce").fillna(0)
    is_leader = (rs_col >= min_rs) & (pct_off_hi <= max_off_hi)
    df["_is_constituent_leader"] = is_leader

    # Filter out Unknown / empty themes for the statistical aggregation
    valid_mask = (
        df["Mapped_Theme"].notna()
        & (df["Mapped_Theme"].astype(str).str.strip() != "")
        & (df["Mapped_Theme"].astype(str).str.strip().str.lower() != "unknown")
    )
    valid_stocks = df[valid_mask]

    if valid_stocks.empty:
        return {}, {}, {}, pd.DataFrame()

    global_leader_rate = valid_stocks["_is_constituent_leader"].mean()
    if pd.isna(global_leader_rate) or global_leader_rate <= 0:
        global_leader_rate = 0.15

    # 1. Group by granular theme for Bottom-Up Breadth
    stats = valid_stocks.groupby("Mapped_Theme").agg(
        total=("Ticker", "count"),
        leaders=("_is_constituent_leader", "sum")
    ).reset_index()

    stats["raw_breadth"] = stats["leaders"] / stats["total"]
    stats["weighted_score"] = (stats["leaders"] + C * global_leader_rate) / (stats["total"] + C)

    max_bu = stats["weighted_score"].max()
    min_bu = stats["weighted_score"].min()
    if max_bu > min_bu:
        stats["BU_Normalized_Score"] = ((stats["weighted_score"] - min_bu) / (max_bu - min_bu)) * 100.0
    else:
        stats["BU_Normalized_Score"] = 50.0

    # 2. Extract Top-Down ETF Macro Score if available
    if top_down_theme_strength is not None and not top_down_theme_strength.empty:
        td_map = dict(zip(
            top_down_theme_strength["Theme"].astype(str).str.strip(),
            pd.to_numeric(top_down_theme_strength["Theme_Strength_Normalized"], errors="coerce").fillna(50.0)
        ))
        
        td_scores = []
        for th in stats["Mapped_Theme"]:
            th_clean = str(th).strip()
            # Direct match
            if th_clean in td_map:
                td_scores.append(td_map[th_clean])
            else:
                # Parent translation match
                parent = str(THEME_TRANSLATION.get(th_clean, th_clean)).strip()
                if parent in td_map:
                    td_scores.append(td_map[parent])
                else:
                    td_scores.append(None)
                    
        stats["TD_Score"] = td_scores
        # Fill missing with BU score so unmapped niche themes still rank purely on their own merits
        stats["TD_Score"] = stats["TD_Score"].fillna(stats["BU_Normalized_Score"])
    else:
        stats["TD_Score"] = stats["BU_Normalized_Score"]
        w_td = 0.0
        w_bu = 1.0

    # 3. Dual-Engine Composite Score
    # Normalize weights if sum != 1.0
    total_w = w_td + w_bu
    if total_w > 0:
        w_td_norm = w_td / total_w
        w_bu_norm = w_bu / total_w
    else:
        w_td_norm, w_bu_norm = 0.5, 0.5

    stats["Composite_Score"] = (w_td_norm * stats["TD_Score"]) + (w_bu_norm * stats["BU_Normalized_Score"])

    # 4. Sort and Classify
    stats = stats.sort_values("Composite_Score", ascending=False).reset_index(drop=True)
    stats["Rank"] = stats.index + 1

    total_themes = len(stats)
    n_leading = max(1, int(round(total_themes * top_pct)))
    n_lagging = max(1, int(round(total_themes * bot_pct)))
    lagging_start_idx = total_themes - n_lagging

    theme_classes = []
    for idx in range(total_themes):
        if idx < n_leading:
            theme_classes.append("Leading")
        elif idx >= lagging_start_idx:
            theme_classes.append("Lagging")
        else:
            theme_classes.append("Neutral")

    stats["Class"] = theme_classes

    theme_class_map = dict(zip(stats["Mapped_Theme"], stats["Class"]))
    theme_score_map = dict(zip(stats["Mapped_Theme"], stats["Composite_Score"]))
    theme_rank_map = dict(zip(stats["Mapped_Theme"], stats["Rank"]))

    return theme_class_map, theme_score_map, theme_rank_map, stats
