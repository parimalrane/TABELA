import json
import os
from typing import Dict, Set

import pandas as pd

from core.config import STOCK_TRANSITION_CONFIG


REGISTRY_FILE = STOCK_TRANSITION_CONFIG["REGISTRY_FILE"]
OBSERVATION_MIN_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MIN_RUNS"]
OBSERVATION_MAX_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MAX_RUNS"]


OBSERVATION = "OBSERVATION"
DISTRIBUTION = "DISTRIBUTION"


# ==========================================================
# Registry
# ==========================================================

def load_registry() -> Dict:

    if not os.path.exists(REGISTRY_FILE):
        return {}

    try:
        with open(REGISTRY_FILE, "r") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}

    except Exception:
        return {}


def save_registry(registry: Dict) -> None:

    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)

    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4, sort_keys=True)


# ==========================================================
# Helpers
# ==========================================================

def _long_ticker_set(long_candidates: pd.DataFrame) -> Set[str]:

    if long_candidates is None or long_candidates.empty:
        return set()

    return {
        str(ticker).replace("*", "").strip().upper()
        for ticker in long_candidates["Ticker"]
    }


from engines.runtime_context import context

def _increment_state_days(registry: Dict) -> None:

    today = str(context.market_date)

    for state in registry.values():

        if state.get("last_market_date") == today:
            continue

        state["state_days"] += 1
        state["last_market_date"] = today

def _remove_recovered(
    registry: Dict,
    long_tickers: Set[str],
) -> Dict:

    recovered = {
        "observation": [],
        "distribution": [],
    }

    remove_list = []

    for ticker, state in registry.items():

        if ticker not in long_tickers:
            continue

        if state["tracking_state"] == OBSERVATION:
            recovered["observation"].append(ticker)

        elif state["tracking_state"] == DISTRIBUTION:
            recovered["distribution"].append(ticker)

        remove_list.append(ticker)


    for ticker in remove_list:
        del registry[ticker]

    return recovered

def _expire_observation(
    registry: Dict,
) -> None:
    """
    Observation stocks are no longer expired here.

    Lifecycle:

        Observation 1..7
            ↓
        Distribution 1..N

    Promotion to Distribution is handled in
    post_distribution_update(). Recoveries are handled by
    _remove_recovered().

    Therefore no Observation stocks should be deleted here.
    """
    return

def _add_new_observations(
    registry: Dict,
    previous_longs: Set[str],
    current_longs: Set[str],
    current_market_date,
) -> None:

    removed_today = previous_longs - current_longs

    for ticker in removed_today:

        if ticker not in registry:

            registry[ticker] = {

                "tracking_state": OBSERVATION,

                "state_days": 1,

                "last_market_date": str(current_market_date),

            }


# ==========================================================
# Public API
# ==========================================================

def pre_distribution_update(
    registry: Dict,
    previous_long_candidates: pd.DataFrame,
    current_long_candidates: pd.DataFrame,
) -> tuple[Dict, Dict]:


    previous_longs = _long_ticker_set(previous_long_candidates)
    current_longs = _long_ticker_set(current_long_candidates)

    _increment_state_days(registry)

    recovered = _remove_recovered(
        registry,
        current_longs,
    )


    _expire_observation(registry)

    _add_new_observations(
        registry,
        previous_longs,
        current_longs,
        context.market_date,
    )

    return registry, recovered

# ==========================================================
# Distribution Candidate Selection
# ==========================================================

def get_distribution_candidates(
    registry: Dict,
    stocks: pd.DataFrame,
) -> pd.DataFrame:

    if stocks is None or stocks.empty:
        return stocks.iloc[0:0].copy()

    eligible = set()

    for ticker, state in registry.items():

        state_days = state.get(
            "state_days",
            state.get("tracking_runs", 0),
        )

        if (
            state["tracking_state"] == OBSERVATION
            and state_days >= OBSERVATION_MIN_RUNS
        ):
            eligible.add(ticker)

    if not eligible:
        return stocks.iloc[0:0].copy()

    return stocks[
        stocks["Ticker"]
        .astype(str)
        .str.upper()
        .isin(eligible)
    ].copy()

# ==========================================================
# Registry Update After Distribution
# ==========================================================

# ==========================================================
# Registry Update After Distribution
# ==========================================================

def post_distribution_update(
    registry: Dict,
    distribution_watchlist: pd.DataFrame,
) -> Dict:
    """
    Observation lifecycle

        Observation 1..7
            ↓
        (next trading day)
            ↓
        Recovered?  -> Remove
        Still weak? -> Distribution 1

    Promotion is controlled by observation age,
    NOT by whether the stock happened to qualify
    for today's distribution watchlist.
    """

    today = str(context.market_date)

    qualified = set()

    if distribution_watchlist is not None and not distribution_watchlist.empty:
        qualified = {
            str(ticker).strip().upper()
            for ticker in distribution_watchlist["Ticker"]
        }

    for ticker, state in list(registry.items()):

        # Only Observation stocks can transition
        if state["tracking_state"] != OBSERVATION:
            continue

        state_days = state.get(
            "state_days",
            state.get("tracking_runs", 0),
        )

        # Stay in Observation through Day 7
        if state_days <= OBSERVATION_MAX_RUNS:
            continue

        # Day 8+
        # Only promote AFTER completing Day 7
        if state_days == OBSERVATION_MAX_RUNS + 1 and ticker in qualified:
            state["tracking_state"] = DISTRIBUTION
            state["state_days"] = 1
            state["last_market_date"] = today
        elif state_days > OBSERVATION_MAX_RUNS:
            del registry[ticker]

    save_registry(registry)

    return registry

# ==========================================================
# Tracking State Helper
# ==========================================================

def apply_tracking_state(
    registry: Dict,
    stocks: pd.DataFrame,
) -> pd.DataFrame:

    if stocks is None or stocks.empty:
        return stocks

    def resolve_state(ticker: str) -> str:

        ticker = str(ticker).strip().upper()

        if ticker in registry:
            return registry[ticker]["tracking_state"]

        return "LONG" if bool(
            stocks.loc[
                stocks["Ticker"] == ticker,
                "Is_Long_Candidate",
            ].iloc[0]
        ) else "UNTRACKED"

    stocks = stocks.copy()

    stocks["Tracking_State"] = (
        stocks["Ticker"]
        .astype(str)
        .str.upper()
        .apply(resolve_state)
    )

    return stocks


def get_transition_summary(registry: Dict) -> Dict:

    observation = []
    distribution = []

    for ticker, state in sorted(registry.items()):

        state_days = state.get(
            "state_days",
            state.get("tracking_runs", 0),
        )

        entry = {
            "ticker": ticker,
            "runs": state_days,
        }

        if state["tracking_state"] == OBSERVATION:
            observation.append(entry)

        elif state["tracking_state"] == DISTRIBUTION:
            distribution.append(entry)

    return {
        "observation": observation,
        "distribution": distribution,
    }


def get_distribution_watchlist(
    registry,
    stocks,
):
    """
    Return all stocks that are currently in the DISTRIBUTION state.
    The registry is the single source of truth.
    """

    distribution_tickers = {
        ticker
        for ticker, state in registry.items()
        if state.get("tracking_state") == DISTRIBUTION
    }

    if not distribution_tickers:
        return pd.DataFrame(columns=stocks.columns)

    return stocks[
        stocks["Ticker"].isin(distribution_tickers)
    ].copy()