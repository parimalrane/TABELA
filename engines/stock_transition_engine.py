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


def _increment_tracking_runs(registry: Dict) -> None:

    for ticker in registry:

        registry[ticker]["tracking_runs"] += 1


def _remove_recovered(
    registry: Dict,
    long_tickers: Set[str]
) -> None:

    remove_list = []

    for ticker in registry:

        if ticker in long_tickers:
            remove_list.append(ticker)

    for ticker in remove_list:
        del registry[ticker]


def _expire_observation(
    registry: Dict
) -> None:

    remove_list = []

    for ticker, state in registry.items():

        if (
            state["tracking_state"] == OBSERVATION
            and state["tracking_runs"] > OBSERVATION_MAX_RUNS
        ):
            remove_list.append(ticker)

    for ticker in remove_list:
        del registry[ticker]


def _add_new_observations(
    registry: Dict,
    previous_longs: Set[str],
    current_longs: Set[str]
) -> None:

    removed_today = previous_longs - current_longs

    for ticker in removed_today:

        if ticker not in registry:

            registry[ticker] = {

                "tracking_state": OBSERVATION,

                "tracking_runs": 1

            }


# ==========================================================
# Public API
# ==========================================================

def pre_distribution_update(
    registry: Dict,
    previous_long_candidates: pd.DataFrame,
    current_long_candidates: pd.DataFrame
) -> Dict:

    previous_longs = _long_ticker_set(previous_long_candidates)

    current_longs = _long_ticker_set(current_long_candidates)

    _increment_tracking_runs(registry)

    _remove_recovered(
        registry,
        current_longs
    )

    _expire_observation(registry)

    _add_new_observations(
        registry,
        previous_longs,
        current_longs
    )

    return registry

# ==========================================================
# Distribution Candidate Selection
# ==========================================================

def get_distribution_candidates(
    registry: Dict,
    stocks: pd.DataFrame,
) -> pd.DataFrame:

    if stocks is None or stocks.empty:
        return stocks.iloc[0:0].copy()

    eligible = {
        ticker
        for ticker, state in registry.items()
        if (
            state["tracking_state"] == OBSERVATION
            and state["tracking_runs"] >= OBSERVATION_MIN_RUNS
        )
    }

    if not eligible:
        return stocks.iloc[0:0].copy()

    return stocks[
        stocks["Ticker"].astype(str).str.upper().isin(eligible)
    ].copy()


# ==========================================================
# Registry Update After Distribution
# ==========================================================

def post_distribution_update(
    registry: Dict,
    distribution_watchlist: pd.DataFrame,
) -> Dict:

    if distribution_watchlist is None or distribution_watchlist.empty:
        save_registry(registry)
        return registry

    qualified = {
        str(ticker).strip().upper()
        for ticker in distribution_watchlist["Ticker"]
    }

    for ticker in qualified:

        if ticker not in registry:
            continue

        registry[ticker]["tracking_state"] = DISTRIBUTION
        registry[ticker]["tracking_runs"] = 1

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
