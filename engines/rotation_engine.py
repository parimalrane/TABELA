import os
import json
from datetime import datetime


SNAPSHOT_DIR = "market_data/snapshots"
ROTATION_DIR = "market_data/rotation_delta"

os.makedirs(ROTATION_DIR, exist_ok=True)


# ==========================================
# LOAD LAST TWO AVAILABLE SNAPSHOTS
# ==========================================

def load_last_two_snapshots():

    files = sorted([
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.endswith(".json")
    ])

    if len(files) < 2:
        return None, None

    previous_file = os.path.join(SNAPSHOT_DIR, files[-2])
    latest_file = os.path.join(SNAPSHOT_DIR, files[-1])

    with open(previous_file, "r") as f:
        previous = json.load(f)

    with open(latest_file, "r") as f:
        latest = json.load(f)

    return previous, latest


# ==========================================
# BUILD THEME → CATEGORY MAP
# ==========================================

def build_theme_category_map(snapshot):

    theme_map = {}

    for theme in snapshot["leading_themes"]:
        theme_map[theme] = "Leading"

    for theme in snapshot["emerging_themes"]:
        theme_map[theme] = "Emerging"

    for theme in snapshot["weakening_themes"]:
        theme_map[theme] = "Weakening"

    for theme in snapshot["lagging_themes"]:
        theme_map[theme] = "Lagging"

    return theme_map


# ==========================================
# CALCULATE ROTATION DELTA
# ==========================================

def calculate_rotation_delta():

    previous, latest = load_last_two_snapshots()

    if previous is None:
        return None

    previous_map = build_theme_category_map(previous)
    latest_map = build_theme_category_map(latest)

    previous_themes = set(previous_map.keys())
    latest_themes = set(latest_map.keys())

    # --------------------------------------
    # NEW ENTRIES
    # --------------------------------------

    new_entries = list(latest_themes - previous_themes)

    # --------------------------------------
    # EXITS
    # --------------------------------------

    exits = list(previous_themes - latest_themes)

    # --------------------------------------
    # CATEGORY CHANGES
    # --------------------------------------

    category_changes = []

    common_themes = previous_themes & latest_themes

    for theme in common_themes:

        old_category = previous_map[theme]
        new_category = latest_map[theme]

        if old_category != new_category:

            category_changes.append({

                "theme": theme,

                "from": old_category,

                "to": new_category

            })

    rotation_data = {

        "date": latest["date"],

        "compared_against": previous["date"],

        "new_entries": sorted(new_entries),

        "exits": sorted(exits),

        "category_changes": category_changes

    }

    return rotation_data


# ==========================================
# SAVE ROTATION DELTA JSON
# ==========================================

def save_rotation_delta(rotation_data):

    if rotation_data is None:
        return

    filename = os.path.join(

        ROTATION_DIR,

        f"{rotation_data['date']}_rotation_delta.json"

    )

    with open(filename, "w") as f:

        json.dump(rotation_data, f, indent=4)

    print()
    print("ROTATION DELTA SAVED:", filename)


# ==========================================
# PRINT REPORT
# ==========================================

def print_rotation_report(rotation_data):

    if rotation_data is None:
        return

    print("\nROTATION DELTA REPORT")
    print("----------------------------")

    print(

        f"Period: "

        f"{rotation_data['compared_against']}"

        f" → "

        f"{rotation_data['date']}"

    )

    print("\nNEW THEME ENTRIES")

    for theme in rotation_data["new_entries"]:

        print(theme)

    print("\nTHEME EXITS")

    for theme in rotation_data["exits"]:

        print(theme)

    print("\nCATEGORY CHANGES")

    for item in rotation_data["category_changes"]:

        print(

            f"{item['theme']} : "

            f"{item['from']} → {item['to']}"

        )