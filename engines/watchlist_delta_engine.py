import os
import json
import datetime


WATCHLIST_DIR = "market_data/watchlist_history"
os.makedirs(WATCHLIST_DIR, exist_ok=True)


def compare_watchlists(current_long, current_short):

    today = str(datetime.date.today())

    current_file = os.path.join(
        WATCHLIST_DIR,
        f"watchlist_{today}.json"
    )

    previous_file = get_previous_watchlist(today)

    # First ever run
    if previous_file is None:

        save_watchlist(
            current_file,
            current_long,
            current_short
        )

        print("\nWATCHLIST DELTA REPORT")
        print("----------------------------")
        print("No previous trading day watchlist found. Baseline created.")

        return

    with open(previous_file, "r") as f:
        old_data = json.load(f)

    old_long = set(old_data["long"])
    old_short = set(old_data["short"])

    current_long = set(current_long)
    current_short = set(current_short)

    new_longs = current_long - old_long
    removed_longs = old_long - current_long

    new_shorts = current_short - old_short
    removed_shorts = old_short - current_short

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
        current_long,
        current_short
    )


def save_watchlist(file_path, long_list, short_list):

    data = {
        "long": list(long_list),
        "short": list(short_list)
    }

    with open(file_path, "w") as f:
        json.dump(data, f)


def get_previous_watchlist(today):

    files = [

        f for f in os.listdir(WATCHLIST_DIR)

        if f.startswith("watchlist_")
        and f.endswith(".json")
        and today not in f
    ]

    if not files:
        return None

    files.sort(reverse=True)

    return os.path.join(
        WATCHLIST_DIR,
        files[0]
    )