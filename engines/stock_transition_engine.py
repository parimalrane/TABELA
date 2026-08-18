import json
import os
from typing import Dict, Set

import pandas as pd

from core.config import (
    DISTRIBUTION_ENGINE_CONFIG,
    STOCK_TRANSITION_CONFIG,
)
from core.runtime_context import context
from engines.watchlist_delta_engine import load_previous_long_watchlist


REGISTRY_DIR = STOCK_TRANSITION_CONFIG["REGISTRY_DIR"]
OBSERVATION_MAX_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MAX_RUNS"]

OBSERVATION = "OBSERVATION"
DISTRIBUTION = "DISTRIBUTION"


def load_registry() -> Dict:
    """
    Load the latest registry strictly before today's market date.
    Supports replay, weekends and holidays.
    """

    os.makedirs(REGISTRY_DIR, exist_ok=True)

    today = str(context.market_date)

    candidates = []

    for filename in os.listdir(REGISTRY_DIR):

        if not filename.endswith("_registry.json"):
            continue

        registry_date = filename.replace("_registry.json", "")

        if registry_date >= today:
            continue

        candidates.append((registry_date, filename))

    if not candidates:
        return {}

    _, latest = max(candidates)

    with open(
        os.path.join(REGISTRY_DIR, latest),
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_registry(registry: Dict) -> None:
    """
    Save today's immutable registry.
    """

    os.makedirs(REGISTRY_DIR, exist_ok=True)

    filename = os.path.join(
        REGISTRY_DIR,
        f"{context.market_date}_registry.json",
    )

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            registry,
            f,
            indent=4,
            sort_keys=True,
        )

def pre_distribution_update(
    registry: Dict,
    current_long_candidates: pd.DataFrame,
    stocks: pd.DataFrame = None,
):
    """
    Lifecycle Phase 1

    Order of operations

    1. Build FINAL current LONG universe.
    2. Load previous LONG universe.
    3. Recover stocks that returned to LONG.
    4. Advance surviving tracked stocks.
    5. Create Observation Day 1 for stocks that left LONG.
    """

    today = str(context.market_date)

    recovered = {
        "observation": [],
        "distribution": [],
        "long": [],
    }

    #
    # FINAL LONG universe
    #
    current_longs = {
        str(t).replace("*", "").strip().upper()
        for t in current_long_candidates["Ticker"]
        if pd.notna(t) and str(t).strip()
    }

    #
    # PREVIOUS LONG universe
    #
    previous = load_previous_long_watchlist()

    previous_longs = (
        {
            str(t).replace("*", "").strip().upper()
            for t in previous["Ticker"]
            if pd.notna(t) and str(t).strip()
        }
        if previous is not None and not previous.empty
        else set()
    )

    #
    # STEP 1
    # Recover stocks now back in LONG.
    #
    recovered_today = set()

    for ticker in list(registry.keys()):
    
        if not ticker or pd.isna(ticker):
            registry.pop(ticker)
            continue

        if ticker not in current_longs:
            continue

        state = registry.pop(ticker)
        
        state_key = state["tracking_state"].lower()
        if state_key not in recovered:
            recovered[state_key] = []

        recovered[state_key].append(ticker)
        recovered_today.add(ticker)

    #
    # STEP 2
    # Advance surviving tracked stocks exactly once.
    # Re-evaluate LONG registry entries to prevent premature demotion
    #
    for ticker, state in list(registry.items()):

        if state.get("last_market_date") == today:
            continue

        if state["tracking_state"] == "LONG":
            if stocks is not None and not stocks.empty:
                match = stocks[stocks["Ticker"].astype(str).str.upper() == ticker]
                if match.empty:
                    # Ghost stock vanished from universe.
                    state["tracking_state"] = OBSERVATION
                    state["state_days"] = 1
                    state["last_market_date"] = today
                    continue

        elif state["tracking_state"] in (OBSERVATION, DISTRIBUTION):
            if stocks is not None and not stocks.empty:
                match = stocks[stocks["Ticker"].astype(str).str.upper() == ticker]
                if match.empty:
                    # Ticker in OBSERVATION/DISTRIBUTION has vanished from
                    # the stocks universe. Log explicitly — do NOT silently
                    # drop from registry; keep advancing state_days so it
                    # remains auditable in the transition report.
                    pass
                    # print(
                    #     f"[TRANSITION WARNING] {ticker} in "
                    #     f"{state['tracking_state']} vanished from stocks "
                    #     f"universe on {today}. Retaining in registry "
                    #     f"(day {state['state_days'] + 1})."
                    # )

        state["state_days"] += 1
        state["last_market_date"] = today

    #
    # STEP 3
    # Stocks that genuinely left LONG today.
    #
    removed_today = (
        previous_longs
        - current_longs
        - recovered_today
    )

    for ticker in removed_today:

        if ticker in registry:
            continue

        vanished_from_universe = False

        if stocks is not None and not stocks.empty:
            match = stocks[stocks["Ticker"].astype(str).str.upper() == ticker]
            if match.empty:
                # Ticker left LONG but is also absent from today's universe.
                vanished_from_universe = True
                pass

        # Unconditionally drop to OBSERVATION since it was removed from LONG
        registry[ticker] = {
            "tracking_state": OBSERVATION,
            "state_days": 1,
            "last_market_date": today,
        }

    return registry, recovered

def get_distribution_candidates(
    registry: Dict,
    stocks: pd.DataFrame,
):
    """
    Observation stocks becoming eligible for Distribution today.
    """

    if stocks.empty:
        return stocks.iloc[0:0].copy()

    eligible = {
        ticker
        for ticker, state in registry.items()
        if (
            state["tracking_state"] == OBSERVATION
            and state["state_days"] == OBSERVATION_MAX_RUNS + 1
        )
    }

    if not eligible:
        return stocks.iloc[0:0].copy()

    return stocks[
        stocks["Ticker"]
        .astype(str)
        .str.upper()
        .isin(eligible)
    ].copy()


def post_distribution_update(
    registry: Dict,
    qualified_distribution: pd.DataFrame,
):
    """
    Finalize Observation lifecycle and persist registry.
    """

    today = str(context.market_date)

    qualified = set()

    if qualified_distribution is not None and not qualified_distribution.empty:
        qualified = {
            str(t).strip().upper()
            for t in qualified_distribution["Ticker"]
        }

    for ticker in list(registry.keys()):

        state = registry[ticker]

        if state["tracking_state"] != OBSERVATION:
            continue

        #
        # Still in Observation window
        #
        if state["state_days"] <= OBSERVATION_MAX_RUNS:
            continue

        #
        # Promote to Distribution
        #
        if ticker in qualified:

            state["tracking_state"] = DISTRIBUTION
            state["state_days"] = 1
            state["last_market_date"] = today
            continue

        #
        # Observation expired
        #
        del registry[ticker]

    save_registry(registry)

    return registry

def get_distribution_watchlist(
    registry: Dict,
    stocks: pd.DataFrame,
):
    """
    Return the active Distribution watchlist.
    """

    if stocks is None or stocks.empty:
        return stocks.iloc[0:0].copy() if stocks is not None else None

    from core.config import DISTRIBUTION_ENGINE_CONFIG
    dist_min_rs = float(DISTRIBUTION_ENGINE_CONFIG.get("DISTRIBUTION_MIN_RS", 40))
    dist_max_days = 20 # Drop short candidates after a month

    distribution = set()
    for ticker in list(registry.keys()):
        state = registry[ticker]
        if state["tracking_state"] == DISTRIBUTION:
            # Check continuous requirements via stocks dataframe
            match = stocks[
                stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker
            ]
            if not match.empty:
                theme = match.iloc[0].get("Theme_Class", "")
                rs = float(match.iloc[0].get("RS_Rating", 0) or 0)
                
                # Rule 2: Cannot short in a Leading theme
                if theme in ["Leading", "Unclassified Leader"]:
                    del registry[ticker]
                    continue
                    
                # Rule 3: The RS Trapdoor
                if rs < dist_min_rs:
                    del registry[ticker]
                    continue
            
            # Rule 4: The Duration Expiration
            if state["state_days"] > dist_max_days:
                del registry[ticker]
                continue
                
            distribution.add(ticker)

    if not distribution:
        return stocks.iloc[0:0].copy()

    df = stocks[
        stocks["Ticker"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .str.strip()
        .str.upper()
        .isin(distribution)
    ].copy()

    # Explicitly warn about DISTRIBUTION tickers absent from today's stocks
    # universe — these were previously silently dropped from output.
    found_in_df = set(
        df["Ticker"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .str.strip()
        .str.upper()
    )
    today = str(context.market_date)
    for ticker in sorted(distribution - found_in_df):
        pass
        # print(
        #     f"[DISTRIBUTION WARNING] {ticker} is in DISTRIBUTION registry "
        #     f"but absent from stocks universe on {today}. "
        #     f"Cannot display in watchlist until it re-enters the universe."
        # )

    for col in [
        "RS_Delta_Val",
        "RS_Trend_Val",
        "Leadership_Loss_Val",
        "History_Val",
        "Composite_Delta_Val",
        "Composite_Trend_Val",
    ]:
        if col not in df.columns:
            df[col] = "-"

    return df

def apply_tracking_state(
    registry: Dict,
    stocks: pd.DataFrame,
):
    """
    Apply registry state to today's stock universe.
    """

    stocks = stocks.copy()

    registry_lookup = {
        ticker: state["tracking_state"]
        for ticker, state in registry.items()
    }

    long_tickers = {
        str(t).strip().upper()
        for t in stocks.loc[
            stocks["Is_Long_Candidate"],
            "Ticker",
        ]
    }

    tracking_state = []

    for ticker in (
        stocks["Ticker"]
        .astype(str)
        .str.replace("*", "", regex=False)
        .str.strip()
        .str.upper()
    ):

        if ticker in registry_lookup:
            tracking_state.append(registry_lookup[ticker])

        elif ticker in long_tickers:
            tracking_state.append("LONG")

        else:
            tracking_state.append("UNTRACKED")

    stocks["Tracking_State"] = tracking_state

    return stocks

def get_transition_summary(
    registry: Dict,
):
    """
    Build transition summary directly from the registry.
    """

    observation = []
    distribution = []

    for ticker in sorted(registry):

        state = registry[ticker]

        entry = {
            "ticker": ticker,
            "runs": state["state_days"],
        }

        if state["tracking_state"] == OBSERVATION:
            observation.append(entry)

        elif state["tracking_state"] == DISTRIBUTION:
            distribution.append(entry)

    return {
        "observation": observation,
        "distribution": distribution,
    }