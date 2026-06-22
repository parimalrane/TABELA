import os
import json
from collections import Counter

SNAPSHOT_DIR = "market_data/snapshots"


# ==========================================
# LOAD ALL SNAPSHOTS
# ==========================================

def load_snapshots():

    files = sorted(
        [
            f for f in os.listdir(SNAPSHOT_DIR)
            if f.endswith(".json")
        ]
    )

    snapshots = []

    for file in files:

        filepath = os.path.join(SNAPSHOT_DIR, file)

        with open(filepath, "r") as f:
            data = json.load(f)

        snapshots.append(data)

    return snapshots


# ==========================================
# STOCK PERSISTENCE
# ==========================================

def stock_persistence_report(snapshots):

    long_counter = Counter()
    short_counter = Counter()

    for snapshot in snapshots:

        for stock in snapshot["top_longs"]:
            long_counter[stock["ticker"]] += 1

        for stock in snapshot["top_shorts"]:
            short_counter[stock["ticker"]] += 1

    repeated_longs = {
        k: v for k, v in long_counter.items()
        if v > 1
    }

    repeated_shorts = {
        k: v for k, v in short_counter.items()
        if v > 1
    }

    return repeated_longs, repeated_shorts


# ==========================================
# FIRST APPEARANCE
# ==========================================

def first_appearance_report(snapshots):

    if len(snapshots) < 2:
        return [], []

    today = snapshots[-1]
    previous = snapshots[:-1]

    historical_longs = set()
    historical_shorts = set()

    for snapshot in previous:

        for stock in snapshot["top_longs"]:
            historical_longs.add(stock["ticker"])

        for stock in snapshot["top_shorts"]:
            historical_shorts.add(stock["ticker"])

    new_longs = []

    for stock in today["top_longs"]:

        ticker = stock["ticker"]

        if ticker not in historical_longs:
            new_longs.append(ticker)

    new_shorts = []

    for stock in today["top_shorts"]:

        ticker = stock["ticker"]

        if ticker not in historical_shorts:
            new_shorts.append(ticker)

    return new_longs, new_shorts


# ==========================================
# THEME PERSISTENCE
# ==========================================

def theme_persistence_report(snapshots):

    theme_counts = {}

    theme_categories = [

        "leading_themes",
        "emerging_themes",
        "weakening_themes",
        "lagging_themes"

    ]

    for category in theme_categories:

        for snapshot in snapshots:

            for theme in snapshot[category]:

                key = (theme, category)

                if key not in theme_counts:
                    theme_counts[key] = 0

                theme_counts[key] += 1

    persistent_themes = {

        k: v for k, v in theme_counts.items()

        if v > 1

    }

    return persistent_themes


# ==========================================
# PRINT REPORT
# ==========================================

def print_persistence_report():

    snapshots = load_snapshots()

    repeated_longs, repeated_shorts = \
        stock_persistence_report(snapshots)

    new_longs, new_shorts = \
        first_appearance_report(snapshots)

    persistent_themes = \
        theme_persistence_report(snapshots)

    print("\n")
    print("==============================================")
    print("TABELA HISTORICAL INTELLIGENCE V0")
    print("==============================================")

    # ------------------------------------------

    print("\nREPEATED LONG LEADERS")
    print("----------------------------")

    for ticker, count in sorted(

        repeated_longs.items(),

        key=lambda x: x[1],

        reverse=True

    )[:15]:

        print(f"{ticker:<10} {count} days")

    # ------------------------------------------

    print("\nREPEATED SHORT CANDIDATES")
    print("----------------------------")

    for ticker, count in sorted(

        repeated_shorts.items(),

        key=lambda x: x[1],

        reverse=True

    )[:15]:

        print(f"{ticker:<10} {count} days")

    # ------------------------------------------

    print("\nNEW LONG ENTRIES")
    print("----------------------------")

    for ticker in new_longs[:10]:

        print(ticker)

    # ------------------------------------------

    print("\nNEW SHORT ENTRIES")
    print("----------------------------")

    for ticker in new_shorts[:10]:

        print(ticker)

    # ------------------------------------------

    print("\nTHEME PERSISTENCE")
    print("----------------------------")

    for (theme, category), count in sorted(

        persistent_themes.items(),

        key=lambda x: x[1],

        reverse=True

    )[:20]:

        label = category.replace("_themes", "")

        print(f"{theme:<30} {label:<12} {count} days")

    print("\n")