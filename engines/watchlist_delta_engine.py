import os
import json
from core.runtime_context import context


WATCHLIST_DIR = "market_data/watchlist_history"
os.makedirs(WATCHLIST_DIR, exist_ok=True)


def build_theme_lookup(stocks):
    """
    Build:
        Ticker -> Theme

    Accepts today's stocks DataFrame.
    """

    lookup = {}

    if stocks is None:
        return lookup
    
    for _, row in stocks.iterrows():

        ticker = str(row["Ticker"]).replace("*", "").strip()

        theme = (
            row.get("ETF_Theme")
            or row.get("Theme")
            or "Unknown"
        )

        lookup[ticker] = theme

    return lookup


def compare_watchlists(
    current_true_long,
    current_pre_obs,
    current_observation,
    current_distribution,
    recovered,
    stocks=None,
):

    today = context.market_date

    current_file = os.path.join(
        WATCHLIST_DIR,
        f"watchlist_{today}.json",
    )

    previous_file = get_previous_watchlist(str(today))

    theme_lookup = build_theme_lookup(stocks)

    current_true_long_set = {
        str(x).replace("*", "").strip()
        for x in current_true_long
    }

    current_pre_obs_set = {
        str(x).replace("*", "").strip()
        for x in current_pre_obs
    }
    
    # Combined for legacy operations
    current_long_set = current_true_long_set | current_pre_obs_set

    current_observation_set = {
        str(x).replace("*", "").strip()
        for x in current_observation
    }

    current_distribution_set = {
        str(x).replace("*", "").strip()
        for x in current_distribution
    }

    #
    # First run
    #

    if previous_file is None:
    
        current_true_long_ordered = [str(x).replace("*", "").strip().upper() for x in current_true_long]
        current_pre_obs_ordered = [str(x).replace("*", "").strip().upper() for x in current_pre_obs]
        current_observation_ordered = [str(x).replace("*", "").strip().upper() for x in current_observation]
        current_distribution_ordered = [str(x).replace("*", "").strip().upper() for x in current_distribution]

        save_watchlist(
            current_file,
            current_true_long_ordered,
            current_pre_obs_ordered,
            current_observation_ordered,
            current_distribution_ordered,
            theme_lookup,
        )

        return {
            "new_longs": [],
            "new_pre_observation": [],
            "new_observation": [],
            "new_distribution": [],
            "left_distribution": [],
            "recovering_observation": [],
            "recovering_distribution": [],
            "movements": {},
        }

    with open(previous_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    def extract_ordered_tickers(items):
        tickers = []
        for item in items:
            if isinstance(item, str):
                t = item.replace("*", "").strip().upper()
            else:
                t = item["ticker"].replace("*", "").strip().upper()
            if t not in tickers:
                tickers.append(t)
        return tickers

    old_true_long_list = extract_ordered_tickers(old_data.get("true_long", old_data.get("long", [])))
    old_pre_obs_list = extract_ordered_tickers(old_data.get("pre_observation", []))
    old_observation_list = extract_ordered_tickers(old_data.get("observation", []))
    old_distribution_list = extract_ordered_tickers(old_data.get("distribution", []))
    
    old_long = set(old_true_long_list) | set(old_pre_obs_list)
    old_true_long = set(old_true_long_list)
    old_pre_obs = set(old_pre_obs_list)
    old_observation = set(old_observation_list)
    old_distribution = set(old_distribution_list)

    #
    # Watchlist deltas
    #
    # New True Longs (Includes brand new entries, and upgrades from Pre-Obs)
    new_longs = sorted(current_true_long_set - old_true_long)

    # Demoted to Pre-Observation today (was a True Long yesterday, is Pre-Obs today)
    new_pre_observation = sorted(current_pre_obs_set - old_pre_obs)

    removed_longs = old_long - current_long_set

    #
    # Only stocks that moved from pipeline memory -> OBSERVATION today
    #
    new_observation = sorted(
        removed_longs & current_observation_set
    )

    new_distribution = sorted(
        current_distribution_set - old_distribution
    )

    left_distribution = sorted(
        old_distribution - current_distribution_set
    )

    #

    #
    recovering_observation = sorted(
        recovered["observation"]
    )

    recovering_distribution = sorted(
        recovered["distribution"]
    )

    def calculate_movements(old_ord, cur_ordered, new_s):
        movs = {}
        for new_idx, t in enumerate(cur_ordered):
            if t in new_s:
                movs[t] = "NA"
            elif t in old_ord:
                old_idx = old_ord.index(t)
                diff = old_idx - new_idx
                if diff > 0:
                    movs[t] = f"+{diff}"
                elif diff < 0:
                    movs[t] = str(diff)
                else:
                    movs[t] = "0"
            else:
                movs[t] = "NA"
        return movs
        
    current_true_long_ordered = [str(x).replace("*", "").strip().upper() for x in current_true_long]
    current_pre_obs_ordered = [str(x).replace("*", "").strip().upper() for x in current_pre_obs]
    current_observation_ordered = [str(x).replace("*", "").strip().upper() for x in current_observation]
    current_distribution_ordered = [str(x).replace("*", "").strip().upper() for x in current_distribution]

    movements = {}
    movements.update(calculate_movements(old_true_long_list, current_true_long_ordered, new_longs))
    movements.update(calculate_movements(old_pre_obs_list, current_pre_obs_ordered, new_pre_observation))
    movements.update(calculate_movements(old_observation_list, current_observation_ordered, new_observation))
    movements.update(calculate_movements(old_distribution_list, current_distribution_ordered, new_distribution))

    save_watchlist(
        current_file,
        current_true_long_ordered,
        current_pre_obs_ordered,
        current_observation_ordered,
        current_distribution_ordered,
        theme_lookup,
    )

    return {
        "new_longs": new_longs,
        "new_pre_observation": new_pre_observation,
        "new_observation": new_observation,
        "new_distribution": new_distribution,
        "left_distribution": left_distribution,
        "recovering_observation": recovering_observation,
        "recovering_distribution": recovering_distribution,
        "movements": movements,
    }

def save_watchlist(
    file_path,
    true_long_list,
    pre_obs_list,
    observation_list,
    distribution_list,
    theme_lookup,
):

    def build_entries(items):
        # Do not sort! Keep sequential rank order!
        return [
            {
                "ticker": ticker,
                "theme": theme_lookup.get(ticker, "Unknown"),
            }
            for ticker in items
        ]

    data = {
        "true_long": build_entries(true_long_list),
        "pre_observation": build_entries(pre_obs_list),
        "long": build_entries(true_long_list + pre_obs_list),  # maintain legacy format
        "observation": build_entries(observation_list),
        "distribution": build_entries(distribution_list),
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
        )

def get_previous_watchlist(today):

    files = [

        f
        for f in os.listdir(WATCHLIST_DIR)

        if f.startswith("watchlist_")
        and f.endswith(".json")
        and f < f"watchlist_{today}.json"

    ]

    if not files:
        return None

    files.sort(reverse=True)

    return os.path.join(
        WATCHLIST_DIR,
        files[0],
    )

def load_previous_long_watchlist():
    """
    Returns the previous trading day's LONG watchlist as a DataFrame
    with a single column: Ticker
    """

    previous_file = get_previous_watchlist(str(context.market_date))

    if previous_file is None:
        import pandas as pd
        return pd.DataFrame(columns=["Ticker"])

    with open(previous_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for item in data.get("long", []):

        if isinstance(item, str):
            ticker = item
        else:
            ticker = item["ticker"]

        rows.append(
            {
                "Ticker": ticker.replace("*", "").strip()
            }
        )

    import pandas as pd
    return pd.DataFrame(rows)