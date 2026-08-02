import json
import os
from typing import Dict, Set

import pandas as pd

from core.config import STOCK_TRANSITION_CONFIG
from core.runtime_context import context
from engines.watchlist_delta_engine import load_previous_long_watchlist


REGISTRY_DIR = STOCK_TRANSITION_CONFIG["REGISTRY_DIR"]
OBSERVATION_MIN_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MIN_RUNS"]
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

        if registry_date > today:
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
    }

    #
    # FINAL LONG universe
    #
    current_longs = {
        str(t).replace("*", "").strip().upper()
        for t in current_long_candidates["Ticker"]
    }

    #
    # PREVIOUS LONG universe
    #
    previous = load_previous_long_watchlist()

    previous_longs = (
        {
            str(t).replace("*", "").strip().upper()
            for t in previous["Ticker"]
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

        if ticker not in current_longs:
            continue

        state = registry.pop(ticker)

        recovered[state["tracking_state"].lower()].append(ticker)
        recovered_today.add(ticker)

    #
    # STEP 2
    # Advance surviving tracked stocks exactly once.
    #
    for state in registry.values():

        if state.get("last_market_date") == today:
            continue

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

    distribution = {
        ticker
        for ticker, state in registry.items()
        if state["tracking_state"] == DISTRIBUTION
    }

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