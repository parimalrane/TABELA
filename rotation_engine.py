import os
import json


# ------------------------------------------
# LOAD LAST TWO SNAPSHOTS
# ------------------------------------------

def load_last_two_snapshots():

    history_folder = "history"

    files = sorted(

        [

            f for f in os.listdir(history_folder)

            if f.endswith(".json")

        ]

    )

    if len(files) < 2:

        return None, None

    previous_file = os.path.join(history_folder, files[-2])
    latest_file = os.path.join(history_folder, files[-1])

    with open(previous_file, "r") as f:
        previous = json.load(f)

    with open(latest_file, "r") as f:
        latest = json.load(f)

    return previous, latest


# ------------------------------------------
# CONVERT SNAPSHOT TO THEME SCORE MAP
# ------------------------------------------

def build_theme_score(snapshot):

    theme_scores = {}

    for theme in snapshot["leading_themes"]:
        theme_scores[theme] = 2

    for theme in snapshot["emerging_themes"]:
        theme_scores[theme] = 1

    for theme in snapshot["weakening_themes"]:
        theme_scores[theme] = -1

    for theme in snapshot["lagging_themes"]:
        theme_scores[theme] = -2

    return theme_scores


# ------------------------------------------
# CALCULATE ROTATION DELTA
# ------------------------------------------

def calculate_rotation_delta():

    previous, latest = load_last_two_snapshots()

    if previous is None:

        return None

    previous_scores = build_theme_score(previous)
    latest_scores = build_theme_score(latest)

    all_themes = set(previous_scores.keys()) | set(latest_scores.keys())

    positive_rotation = []
    negative_rotation = []
    new_entries = []
    dropped_entries = []

    for theme in all_themes:

        old_score = previous_scores.get(theme, 0)
        new_score = latest_scores.get(theme, 0)

        delta = new_score - old_score

        # Theme entered ranking universe today
        if theme not in previous_scores:

            new_entries.append(theme)

        # Theme removed from ranking universe today
        elif theme not in latest_scores:

            dropped_entries.append(theme)

        # Positive movement
        elif delta > 0:

            positive_rotation.append((theme, delta))

        # Negative movement
        elif delta < 0:

            negative_rotation.append((theme, delta))

    positive_rotation = sorted(

        positive_rotation,
        key=lambda x: x[1],
        reverse=True

    )

    negative_rotation = sorted(

        negative_rotation,
        key=lambda x: x[1]

    )

    return {

        "positive_rotation": positive_rotation,
        "negative_rotation": negative_rotation,
        "new_entries": new_entries,
        "dropped_entries": dropped_entries,
        "previous_date": previous["date"],
        "latest_date": latest["date"]

    }


# ------------------------------------------
# PRINT REPORT
# ------------------------------------------

def print_rotation_report(rotation_data):

    if rotation_data is None:

        return

    print("\nROTATION DELTA REPORT")
    print("----------------------------")

    print(
        f"Period: {rotation_data['previous_date']} → {rotation_data['latest_date']}"
    )

    print("\nACCELERATING THEMES")

    for theme, delta in rotation_data["positive_rotation"]:

        print(f"{theme} (+{delta})")

    print("\nWEAKENING THEMES")

    for theme, delta in rotation_data["negative_rotation"]:

        print(f"{theme} ({delta})")

    print("\nNEWLY RANKED THEMES")

    for theme in rotation_data["new_entries"]:

        print(theme)

    print("\nREMOVED FROM RANKING")

    for theme in rotation_data["dropped_entries"]:

        print(theme)