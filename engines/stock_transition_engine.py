print("STOCK TRANSITION FILE:", __file__)
import json
import os
from typing import Dict, Set

import pandas as pd

from core.config import STOCK_TRANSITION_CONFIG

REGISTRY_DIR = STOCK_TRANSITION_CONFIG["REGISTRY_DIR"]
OBSERVATION_MIN_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MIN_RUNS"]
OBSERVATION_MAX_RUNS = STOCK_TRANSITION_CONFIG["OBSERVATION_MAX_RUNS"]


OBSERVATION = "OBSERVATION"
DISTRIBUTION = "DISTRIBUTION"


# ==========================================================
# Registry
# ==========================================================

def load_registry() -> Dict:
    """
    Load the latest registry before the current market date.
    """

    os.makedirs(REGISTRY_DIR, exist_ok=True)

    registry_files = sorted(
        f
        for f in os.listdir(REGISTRY_DIR)
        if f.endswith("_registry.json")
    )

    if not registry_files:
        return {}

    today = str(context.market_date)

    previous_file = None

    for filename in registry_files:
        registry_date = filename.replace("_registry.json", "")

        if registry_date < today:
            previous_file = filename
        else:
            break

    if previous_file is None:
        return {}

    registry_path = os.path.join(REGISTRY_DIR, previous_file)

    with open(registry_path, "r") as f:
        return json.load(f)


def save_registry(registry: Dict) -> None:
    """
    Save today's immutable registry.

    File format:
        market_data/stock_transition/YYYY-MM-DD_registry.json
    """

    os.makedirs(REGISTRY_DIR, exist_ok=True)

    registry_path = os.path.join(
        REGISTRY_DIR,
        f"{context.market_date}_registry.json",
    )

    with open(registry_path, "w") as f:
        json.dump(
            registry,
            f,
            indent=4,
            sort_keys=True,
        )

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

# ==========================================================================
# Replace these functions in engines/stock_transition_engine.py
#
#   _long_ticker_set()
#   + add _load_skip_distribution_list()
#   + add _advance_lifecycle()
#   pre_distribution_update()
#
# Leave everything else unchanged for Batch 1.
# ==========================================================================

from engines.runtime_context import context


def _long_ticker_set(long_candidates: pd.DataFrame) -> Set[str]:

    if long_candidates is None or long_candidates.empty:
        return set()

    return {
        str(ticker).replace("*", "").strip().upper()
        for ticker in long_candidates["Ticker"]
    }


def _load_skip_distribution_list() -> Set[str]:

    filename = os.path.join("data", "skip_distribution.csv")

    if not os.path.exists(filename):
        return set()

    try:

        df = pd.read_csv(filename)

        if "Ticker" not in df.columns:
            return set()

        return {
            str(t).strip().upper()
            for t in df["Ticker"]
            if pd.notna(t)
        }

    except Exception:
        return set()


def _advance_lifecycle(
    registry: Dict,
    previous_longs: Set[str],
    current_longs: Set[str],
) -> Dict:

    today = str(context.market_date)

    recovered = {
        "observation": [],
        "distribution": [],
    }

    skip_distribution = _load_skip_distribution_list()

    #
    # Existing tracked stocks
    #
    for ticker in list(registry.keys()):

        state = registry[ticker]

        #
        # Recover immediately
        #
        if ticker in current_longs:

            if state["tracking_state"] == OBSERVATION:
                recovered["observation"].append(ticker)
            else:
                recovered["distribution"].append(ticker)

            del registry[ticker]
            continue

        #
        # Advance once per market day
        #
        if state.get("last_market_date") != today:
            state["state_days"] += 1
            state["last_market_date"] = today

        
        continue

    #
    # New Observation entries
    #
    removed_today = previous_longs - current_longs

    for ticker in removed_today:

        if ticker in registry:
            continue

        registry[ticker] = {
            "tracking_state": OBSERVATION,
            "state_days": 1,
            "last_market_date": today,
        }

    return recovered


def pre_distribution_update(
    registry: Dict,
    previous_long_candidates: pd.DataFrame,
    current_long_candidates: pd.DataFrame,
) -> tuple[Dict, Dict]:

    previous_longs = _long_ticker_set(previous_long_candidates)
    current_longs = _long_ticker_set(current_long_candidates)

    recovered = _advance_lifecycle(
        registry,
        previous_longs,
        current_longs,
    )

    return registry, recovered

# ==========================================================================
# Replace these functions in engines/stock_transition_engine.py
#
#   get_distribution_candidates()
#   post_distribution_update()
#
# ==========================================================================

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
            state.get("tracking_state") == OBSERVATION
            and state.get("state_days", 0) > OBSERVATION_MAX_RUNS
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
    distribution_watchlist: pd.DataFrame,
) -> Dict:
    """
    Finalize Observation lifecycle after the Distribution engine has
    evaluated all eligible Day 8 stocks.

    Rules:
      - Observation Day 1-7 : remain Observation
      - Observation Day 8:
            * qualified -> Distribution Day 1
            * skip list -> remove
            * otherwise -> remove
    """

    today = str(context.market_date)

    skip_distribution = _load_skip_distribution_list()

    qualified = set()

    if distribution_watchlist is not None and not distribution_watchlist.empty:
        qualified = {
            str(t).strip().upper()
            for t in distribution_watchlist["Ticker"]
        }

    for ticker in list(registry.keys()):

        state = registry[ticker]

        if state["tracking_state"] != OBSERVATION:
            continue

        if state["state_days"] <= OBSERVATION_MAX_RUNS:
            continue

        #
        # Day 8+
        #
        if ticker in skip_distribution:
            del registry[ticker]
            continue

        if ticker in qualified:
            state["tracking_state"] = DISTRIBUTION
            state["state_days"] = 1
            state["last_market_date"] = today
        else:
            del registry[ticker]

    save_registry(registry)

    return registry

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



# ==========================================================================
# Replace these functions in engines/stock_transition_engine.py
#
#   get_transition_summary()
#   get_distribution_watchlist()
#
# ==========================================================================

def get_transition_summary(registry: Dict) -> Dict:

    observation = []
    distribution = []

    for ticker, state in sorted(registry.items()):

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

def get_distribution_watchlist(
    registry: Dict,
    qualified_distribution: pd.DataFrame,
) -> pd.DataFrame:

    if qualified_distribution is None or qualified_distribution.empty:
        return qualified_distribution

    distribution = {
        ticker
        for ticker, state in registry.items()
        if state["tracking_state"] == DISTRIBUTION
    }

    if not distribution:
        return qualified_distribution.iloc[0:0].copy()

    return qualified_distribution[
        qualified_distribution["Ticker"]
        .astype(str)
        .str.upper()
        .isin(distribution)
    ].copy()