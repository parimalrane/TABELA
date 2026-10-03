import json
import os
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
from pathlib import Path

from config.config import (
    LONG_ENTRY,
    SHORT_ENTRY
)
from config.runtime_context import context, get_monthly_path
from reporting.watchlist_delta_engine import load_previous_long_watchlist


REGISTRY_DIR = "market_data/stock_transition"
PURGED_ACCUMULATOR_PATH = Path("market_data") / "purged_accumulator.json"

OBSERVATION = "OBSERVATION"
DISTRIBUTION = "DISTRIBUTION"
LONG = "LONG"


def _normalize_ticker(ticker) -> str:
    if ticker is None or pd.isna(ticker):
        return ""
    return str(ticker).replace("*", "").replace("^", "").replace("~", "").strip().upper()


def load_purged_accumulator() -> Dict:
    """Return the purged-memory tracker {long_purged: {...}, short_purged: {...}}."""
    if not PURGED_ACCUMULATOR_PATH.exists():
        return {"long_purged": {}, "short_purged": {}}

    try:
        with open(PURGED_ACCUMULATOR_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"long_purged": {}, "short_purged": {}}

    normalized = {"long_purged": {}, "short_purged": {}}
    for side_key, bucket in [("long_purged", "long_purged"), ("short_purged", "short_purged")]:
        raw_bucket = data.get(side_key, {}) if isinstance(data, dict) else {}
        if not isinstance(raw_bucket, dict):
            continue
        for ticker, entry in raw_bucket.items():
            clean_ticker = _normalize_ticker(ticker)
            if not clean_ticker:
                continue
            if isinstance(entry, dict):
                record = {"days_purged": int(entry.get("days_purged", 1) or 1), "purged_on": entry.get("purged_on", str(context.market_date))}
            else:
                record = {"days_purged": 1, "purged_on": str(context.market_date)}
            normalized[bucket][clean_ticker] = record
    return normalized


def save_purged_accumulator(accumulator: Dict) -> None:
    PURGED_ACCUMULATOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PURGED_ACCUMULATOR_PATH, "w", encoding="utf-8") as f:
        json.dump(accumulator, f, indent=4, sort_keys=True)


def register_purged_ticker(ticker: str, side: str, market_date=None) -> Dict:
    """Register a stock as purged when it leaves active or waitlist memory."""
    clean_ticker = _normalize_ticker(ticker)
    if not clean_ticker:
        return load_purged_accumulator()

    bucket_key = "long_purged" if str(side).upper() == "LONG" else "short_purged"
    accumulator = load_purged_accumulator()
    today = str(market_date or getattr(context, "market_date", datetime.today().strftime("%Y-%m-%d")))

    existing = accumulator.get(bucket_key, {}).get(clean_ticker)
    if isinstance(existing, dict):
        existing["days_purged"] = max(int(existing.get("days_purged", 1) or 1), 1)
        existing["purged_on"] = existing.get("purged_on", today)
        existing["last_seen"] = today
    else:
        accumulator.setdefault(bucket_key, {})[clean_ticker] = {
            "days_purged": 1,
            "purged_on": today,
            "last_seen": today,
        }

    save_purged_accumulator(accumulator)
    return accumulator


def advance_purged_accumulator(market_date=None) -> Dict:
    """Increment the age of every purged ticker and retire anything older than 50 days."""
    accumulator = load_purged_accumulator()
    today = str(market_date or getattr(context, "market_date", datetime.today().strftime("%Y-%m-%d")))

    for bucket_key in ("long_purged", "short_purged"):
        for ticker, record in list(accumulator.get(bucket_key, {}).items()):
            if not isinstance(record, dict):
                continue
            current_days = int(record.get("days_purged", 1) or 1) + 1
            if current_days >= 51:
                accumulator[bucket_key].pop(ticker, None)
                continue
            record["days_purged"] = current_days
            record["last_seen"] = today
            accumulator[bucket_key][ticker] = record

    save_purged_accumulator(accumulator)
    return accumulator


def sync_purged_memory(registry: Dict, active_tickers=None, waitlist_tickers=None) -> Dict:
    """Any stock that leaves the active/waitlist memory will be persisted in the purged accumulator."""
    active_set = set()
    for candidate_group in (active_tickers or (), waitlist_tickers or ()):
        for ticker in candidate_group:
            clean_ticker = _normalize_ticker(ticker)
            if clean_ticker:
                active_set.add(clean_ticker)

    for ticker, state in list(registry.items()):
        clean_ticker = _normalize_ticker(ticker)
        if not clean_ticker:
            continue
        tracking_state = state.get("tracking_state") if isinstance(state, dict) else ""
        if tracking_state in {LONG, DISTRIBUTION} and clean_ticker not in active_set:
            side = "LONG" if tracking_state == LONG else "SHORT"
            register_purged_ticker(clean_ticker, side, getattr(context, "market_date", None))
            del registry[ticker]

    return registry


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
    
    short_rs = float(row.get("Short_RS_Rating", 0) or 0)
    short_score = float(row.get("Short_Score", 0) or 0)
    
    theme = str(row.get("Theme_Class", ""))

    if "MIN_RS" in criteria_dict:
        if rs < criteria_dict["MIN_RS"]: return False
    if "MAX_RS" in criteria_dict:
        if rs > criteria_dict["MAX_RS"]: return False

    if "MIN_LONG_SCORE" in criteria_dict:
        if score < criteria_dict["MIN_LONG_SCORE"]: return False
    if "MAX_LONG_SCORE" in criteria_dict:
        if score > criteria_dict["MAX_LONG_SCORE"]: return False
        
    if "MIN_SHORT_RS" in criteria_dict:
        if short_rs < criteria_dict["MIN_SHORT_RS"]: return False
    if "MAX_SHORT_RS" in criteria_dict:
        if short_rs > criteria_dict["MAX_SHORT_RS"]: return False
        
    if "MAX_SHORT_SCORE" in criteria_dict:
        if short_score > criteria_dict["MAX_SHORT_SCORE"]: return False

    if "THEMES" in criteria_dict:
        if theme not in criteria_dict["THEMES"]: return False

    if "BLOCKED_ZACKS" in criteria_dict:
        zacks_raw = row.get("Zacks Rank", 0)
        try:
            zacks_val = int(float(zacks_raw)) if pd.notna(zacks_raw) else 0
        except (ValueError, TypeError):
            zacks_val = 0
        if zacks_val in criteria_dict["BLOCKED_ZACKS"]: return False

    if "MIN_PRICE" in criteria_dict:
        price_raw = row.get("Last Close", 0)
        try:
            price_val = float(price_raw) if pd.notna(price_raw) else 0.0
        except (ValueError, TypeError):
            price_val = 0.0
        if price_val < criteria_dict["MIN_PRICE"]: return False

    if "MIN_VOLUME" in criteria_dict:
        vol_raw = row.get("Avg Volume", 0)
        try:
            vol_val = float(vol_raw) if pd.notna(vol_raw) else 0.0
        except (ValueError, TypeError):
            vol_val = 0.0
        if vol_val < criteria_dict["MIN_VOLUME"]: return False

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
            if not _meets_criteria(row, SHORT_ENTRY):
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
            elif _meets_criteria(row, SHORT_ENTRY):
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

    advance_purged_accumulator(context.market_date)
    sync_purged_memory(updated_registry, active_tickers=current_longs, waitlist_tickers=set())
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
        if _meets_criteria(row, SHORT_ENTRY):
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
    advance_purged_accumulator(context.market_date)
    sync_purged_memory(registry, active_tickers=set(), waitlist_tickers=qualified)
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