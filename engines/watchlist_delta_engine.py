import os
import json
from engines.runtime_context import context


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
    current_long,
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

    current_long_set = {
        str(x).replace("*", "").strip()
        for x in current_long
    }

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

        save_watchlist(
            current_file,
            current_long_set,
            current_observation_set,
            current_distribution_set,
            theme_lookup,
        )

        print("\nWATCHLIST DELTA")
        print("----------------------------------------")
        print("Baseline created.")

        return

    with open(previous_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    def extract_tickers(items):

        tickers = set()

        for item in items:

            if isinstance(item, str):
                tickers.add(item.replace("*", "").strip())

            else:
                tickers.add(
                    item["ticker"]
                    .replace("*", "")
                    .strip()
                )

        return tickers

    old_long = extract_tickers(old_data.get("long", []))
    old_observation = extract_tickers(old_data.get("observation", []))
    old_distribution = extract_tickers(old_data.get("distribution", []))

    #
    #
    # Watchlist deltas
    #

    new_longs = sorted(current_long_set - old_long)

    removed_longs = old_long - current_long_set

    #
    # Only stocks that moved from LONG -> OBSERVATION today
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
    recovering_observation = sorted(
        recovered["observation"]
    )

    recovering_distribution = sorted(
        recovered["distribution"]
    )

    print("\nWATCHLIST DELTA")
    print("----------------------------------------")

    print(
        f"Long         (+{len(new_longs)}) : "
        + (", ".join(new_longs) if new_longs else "None")
    )

    print(
        f"Observation  (+{len(new_observation)}) : "
        + (", ".join(new_observation) if new_observation else "None")
    )

    print(
        f"Distribution (+{len(new_distribution)}) : "
        + (", ".join(new_distribution) if new_distribution else "None")
    )

    print(
        f"Left Dist    (-{len(left_distribution)}) : "
        + (", ".join(left_distribution) if left_distribution else "None")
    )

    print()
    print("RECOVERING LEADERS")
    print("----------------------------------------")

    print(
        "Observation : "
        + (
            ", ".join(recovering_observation)
            if recovering_observation else "None"
        )
    )

    print(
        "Distribution: "
        + (
            ", ".join(recovering_distribution)
            if recovering_distribution else "None"
        )
    )


    save_watchlist(
        current_file,
        current_long_set,
        current_observation_set,
        current_distribution_set,
        theme_lookup,
    )

def save_watchlist(
    file_path,
    long_list,
    observation_list,
    distribution_list,
    theme_lookup,
):

    def build_entries(items):

        return [
            {
                "ticker": ticker,
                "theme": theme_lookup.get(
                    ticker,
                    "Unknown",
                ),
            }
            for ticker in sorted(items)
        ]

    data = {
        "long": build_entries(long_list),
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
        and today not in f

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