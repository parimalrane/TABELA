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
    weakness_counter = Counter()

    for snapshot in snapshots:

        for stock in snapshot["top_longs"]:
            long_counter[stock["ticker"]] += 1

        for stock in snapshot["top_weakness"]:
            weakness_counter[stock["ticker"]] += 1

    repeated_longs = {
        k: v for k, v in long_counter.items()
        if v > 1
    }

    repeated_weakness = {
        k: v for k, v in weakness_counter.items()
        if v > 1
    }

    return repeated_longs, repeated_weakness


# ==========================================
# FIRST APPEARANCE
# ==========================================

def first_appearance_report(snapshots):

    if len(snapshots) < 2:
        return [], []

    today = snapshots[-1]
    previous = snapshots[:-1]

    historical_longs = set()
    historical_weakness = set()

    for snapshot in previous:

        for stock in snapshot["top_longs"]:
            historical_longs.add(stock["ticker"])

        for stock in snapshot["top_weakness"]:
            historical_weakness.add(stock["ticker"])

    new_longs = []

    for stock in today["top_longs"]:

        ticker = stock["ticker"]

        if ticker not in historical_longs:
            new_longs.append(ticker)

    new_weakness = []

    for stock in today["top_weakness"]:

        ticker = stock["ticker"]

        if ticker not in historical_weakness:
            new_weakness.append(ticker)

    return new_longs, new_weakness


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

    repeated_longs, repeated_weakness = \
        stock_persistence_report(snapshots)

    new_longs, new_weakness = \
        first_appearance_report(snapshots)

    persistent_themes = \
        theme_persistence_report(snapshots)

    print("\n")
    print("==============================================")
    print("TABELA HISTORICAL INTELLIGENCE V0")
    print("==============================================")

    print("\nREPEATED LONG LEADERS")
    print("----------------------------")

    for ticker, count in sorted(

        repeated_longs.items(),

        key=lambda x: x[1],

        reverse=True

    )[:15]:

        print(f"{ticker:<10} {count} days")

    print("\nREPEATED WEAKNESS CANDIDATES")
    print("----------------------------")

    for ticker, count in sorted(

        repeated_weakness.items(),

        key=lambda x: x[1],

        reverse=True

    )[:15]:

        print(f"{ticker:<10} {count} days")

    print("\nNEW LONG ENTRIES")
    print("----------------------------")

    for ticker in new_longs[:10]:
        print(ticker)

    print("\nNEW WEAKNESS ENTRIES")
    print("----------------------------")

    for ticker in new_weakness[:10]:
        print(ticker)

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