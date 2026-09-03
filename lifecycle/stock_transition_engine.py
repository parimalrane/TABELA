import json
import os
from typing import Dict, Tuple

import pandas as pd
from pathlib import Path

from config.config import (
    LONG_ENTRY,
    DIST_ENTRY
)
from config.runtime_context import context, get_monthly_path
from reporting.watchlist_delta_engine import load_previous_long_watchlist


REGISTRY_DIR = "market_data/stock_transition"

OBSERVATION = "OBSERVATION"
DISTRIBUTION = "DISTRIBUTION"
LONG = "LONG"


def load_registry() -> Dict:
    """
    Load the latest registry strictly before today's market date.
    Holds {ticker: {"tracking_state": "LONG" | "DISTRIBUTION" | "OBSERVATION"}}
    """
    registry_path = Path(REGISTRY_DIR)
    if not registry_path.exists():
        registry_path.mkdir(parents=True, exist_ok=True)

    today = str(context.market_date)
    candidates = []

    for filepath in registry_path.rglob("*_registry.json"):
        filename = filepath.name
        registry_date = filename.replace("_registry.json", "")

        if registry_date >= today:
            continue

        candidates.append((registry_date, filepath))

    if not candidates:
        return {}

    _, latest_path = max(candidates, key=lambda x: x[0])

    with open(latest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data


def save_registry(registry: Dict) -> None:
    """
    Save today's immutable registry.
    """
    target_dir = get_monthly_path(REGISTRY_DIR, context.market_date)
    filename = os.path.join(target_dir, f"{context.market_date}_registry.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, sort_keys=True)


def _meets_criteria(row, criteria_dict):
    """
    Helper to check if a row meets entry or maintain criteria.
    """
    rs = float(row.get("RS_Rating", 0) or 0)
    score = float(row.get("Long_Score", 0) or 0)
    theme = str(row.get("Theme_Class", ""))

    if "MIN_RS" in criteria_dict:
        if rs < criteria_dict["MIN_RS"]: return False
    if "MAX_RS" in criteria_dict:
        if rs > criteria_dict["MAX_RS"]: return False

    if "MIN_LONG_SCORE" in criteria_dict:
        if score < criteria_dict["MIN_LONG_SCORE"]: return False
    if "MAX_LONG_SCORE" in criteria_dict:
        if score > criteria_dict["MAX_LONG_SCORE"]: return False

    if "THEMES" in criteria_dict:
        if theme not in criteria_dict["THEMES"]: return False

    return True

def pre_distribution_update(registry: Dict, current_long_candidates: pd.DataFrame, stocks: pd.DataFrame = None) -> Tuple[Dict, Dict]:
    """
    Evaluates hysteresis for LONG candidates and builds basic state transitions.
    """
    today = str(context.market_date)
    recovered = {"observation": [], "distribution": [], "long": []}
    
    current_longs = {
        str(t).replace("*", "").strip().upper()
        for t in current_long_candidates["Ticker"]
        if pd.notna(t) and str(t).strip()
    }

    # Re-evaluate all stocks in registry
    updated_registry = {}
    
    for ticker, state in registry.items():
        if not ticker or pd.isna(ticker):
            continue
            
        old_state = state["tracking_state"]
        days_in_state = state.get("days_in_state", 1) + 1
        
        match = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker] if stocks is not None else pd.DataFrame()
        
        if match.empty:
            # Dropped from universe, maintain clock
            updated_registry[ticker] = {"tracking_state": OBSERVATION, "days_in_state": days_in_state}
            continue
        row = match.iloc[0]
        new_state = old_state
        grace_days = state.get("grace_days", 0)
        
        if old_state == LONG:
            if not _meets_criteria(row, LONG_ENTRY):
                new_state = OBSERVATION
                days_in_state = 1
            else:
                new_state = LONG
                days_in_state += 1
        elif old_state == DISTRIBUTION:
            if not _meets_criteria(row, DIST_ENTRY):
                new_state = OBSERVATION
                days_in_state = 1
                grace_days = 0
            # Distribution does not expire via time.
        elif old_state == OBSERVATION:
            if _meets_criteria(row, LONG_ENTRY):
                new_state = LONG
                days_in_state = 1
                grace_days = 0
                recovered[old_state.lower()].append(ticker)
            elif _meets_criteria(row, DIST_ENTRY):
                new_state = DISTRIBUTION
                days_in_state = 1
                grace_days = 0
                recovered[old_state.lower()].append(ticker)
            elif days_in_state > 21:
                # Time expiry to prevent permanent list clutter
                new_state = "UNTRACKED"
                continue
                
        # If the stock remains in observation and crosses 21 days
        if new_state == OBSERVATION and days_in_state > 21:
            continue
                
        updated_registry[ticker] = {"tracking_state": new_state, "days_in_state": days_in_state}

        
    for ticker in current_longs:
        if ticker not in updated_registry or updated_registry[ticker]["tracking_state"] != LONG:
            updated_registry[ticker] = {"tracking_state": LONG, "days_in_state": 1}
            if ticker in registry:
                recovered[registry[ticker]["tracking_state"].lower()].append(ticker)

    return updated_registry, recovered


def get_distribution_candidates(registry: Dict, stocks: pd.DataFrame) -> pd.DataFrame:
    """
    Identify true short candidates using hysteresis entry/maintain rules.
    """
    if stocks.empty:
        return stocks.iloc[0:0].copy()

    eligible = set()
    
    for _, row in stocks.iterrows():
        ticker = str(row["Ticker"]).replace("*", "").strip().upper()
        
        # Uses strict entry for all states, no hysteresis
        if _meets_criteria(row, DIST_ENTRY):
            eligible.add(ticker)

    if not eligible:
        return stocks.iloc[0:0].copy()

    return stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(eligible)].copy()


def post_distribution_update(registry: Dict, qualified_distribution: pd.DataFrame, stocks: pd.DataFrame) -> Dict:
    """
    Finalize short candidates into registry.
    """
    qualified = set()
    if qualified_distribution is not None and not qualified_distribution.empty:
        qualified = {str(t).replace("*", "").strip().upper() for t in qualified_distribution["Ticker"]}

    # Update DISTRIBUTION tags
    for ticker in list(registry.keys()):
        if registry[ticker]["tracking_state"] == DISTRIBUTION and ticker not in qualified:
            # Failed to maintain
            registry[ticker]["tracking_state"] = OBSERVATION
            registry[ticker]["days_in_state"] = 1
            
    for ticker in qualified:
        if ticker not in registry:
            registry[ticker] = {"tracking_state": DISTRIBUTION, "days_in_state": 1}
        elif registry[ticker]["tracking_state"] != DISTRIBUTION:
            registry[ticker]["tracking_state"] = DISTRIBUTION
            registry[ticker]["days_in_state"] = 1
        
    # Clean registry (Remove unneeded OBSERVATION objects maybe? No, we need observation to know what just fell)
    # Actually, if we keep observation permanently, it grows.
    # Let's keep it simple: just save.
    save_registry(registry)
    return registry


def get_distribution_watchlist(registry: Dict, stocks: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the actively shorted tickers.
    """
    if stocks is None or stocks.empty:
        return stocks.iloc[0:0].copy() if stocks is not None else None

    distribution = {t for t, s in registry.items() if s["tracking_state"] == DISTRIBUTION}

    if not distribution:
        return stocks.iloc[0:0].copy()

    df = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(distribution)].copy()

    for col in [
        "RS_Delta_Val", "RS_Trend_Val", "Leadership_Loss_Val",
        "History_Val", "Composite_Delta_Val", "Composite_Trend_Val",
    ]:
        if col not in df.columns:
            df[col] = "-"

    return df


def apply_tracking_state(registry: Dict, stocks: pd.DataFrame) -> pd.DataFrame:
    stocks = stocks.copy()
    registry_lookup = {ticker: state["tracking_state"] for ticker, state in registry.items()}
    long_tickers = {str(t).strip().upper() for t in stocks.loc[stocks["Is_Long_Candidate"], "Ticker"]}

    tracking_state = []
    for ticker in stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.strip().str.upper():
        if ticker in registry_lookup:
            tracking_state.append(registry_lookup[ticker])
        elif ticker in long_tickers:
            tracking_state.append("LONG")
        else:
            tracking_state.append("UNTRACKED")

    stocks["Tracking_State"] = tracking_state
    return stocks


def get_transition_summary(registry: Dict) -> Dict:
    observation = [{"ticker": t, "runs": 1} for t, s in registry.items() if s["tracking_state"] == OBSERVATION]
    distribution = [{"ticker": t, "runs": 1} for t, s in registry.items() if s["tracking_state"] == DISTRIBUTION]
    return {"observation": observation, "distribution": distribution}