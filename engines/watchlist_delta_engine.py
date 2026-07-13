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
    current_short,
    stocks=None,
):

    today = context.market_date

    current_file = os.path.join(
        WATCHLIST_DIR,
        f"watchlist_{context.market_date}.json",
    )

    previous_file = get_previous_watchlist(str(today))

    theme_lookup = build_theme_lookup(stocks)

    #
    # Convert today's watchlists to ticker sets
    #

    current_long_set = {
        str(x).replace("*", "").strip()
        for x in current_long
    }

    current_short_set = {
        str(x).replace("*", "").strip()
        for x in current_short
    }

    #
    # First ever run
    #

    if previous_file is None:

        save_watchlist(
            current_file,
            current_long_set,
            current_short_set,
            theme_lookup,
        )

        print("\nWATCHLIST DELTA REPORT")
        print("----------------------------")
        print("No previous trading day watchlist found. Baseline created.")

        return

    with open(previous_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    #
    # Support both old JSON schema
    # ["NVDA","AMD"]
    #
    # and new schema
    # [{"ticker":"NVDA","theme":"Semiconductors"}]
    #

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
    old_short = extract_tickers(old_data.get("short", []))

    new_longs = current_long_set - old_long
    removed_longs = old_long - current_long_set

    new_shorts = current_short_set - old_short
    removed_shorts = old_short - current_short_set

    print("\nWATCHLIST DELTA REPORT")
    print("----------------------------")

    print("\nNEW LONGS ADDED TODAY")
    print(",".join(sorted(new_longs)) if new_longs else "None")

    print("\nLONGS REMOVED TODAY")
    print(",".join(sorted(removed_longs)) if removed_longs else "None")

    print("\nNEW SHORTS ADDED TODAY")
    print(",".join(sorted(new_shorts)) if new_shorts else "None")

    print("\nSHORTS REMOVED TODAY")
    print(",".join(sorted(removed_shorts)) if removed_shorts else "None")

    save_watchlist(
        current_file,
        current_long_set,
        current_short_set,
        theme_lookup,
    )


def save_watchlist(
    file_path,
    long_list,
    short_list,
    theme_lookup,
):

    def build_entries(items):

        entries = []

        for ticker in sorted(items):

            entries.append(
                {
                    "ticker": ticker,
                    "theme": theme_lookup.get(
                        ticker,
                        "Unknown",
                    ),
                }
            )

        return entries

    data = {
        "long": build_entries(long_list),
        "short": build_entries(short_list),
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