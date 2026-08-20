import os
import json
from datetime import datetime
from pathlib import Path

from config.runtime_context import get_monthly_path

SNAPSHOT_DIR = Path("market_data/snapshots")
ROTATION_DIR = Path("market_data/rotation_delta")

# ==========================================
# LOAD LAST TWO AVAILABLE SNAPSHOTS
# ==========================================

def load_last_two_snapshots():

    if not SNAPSHOT_DIR.exists():
        return None, None

    files = sorted(SNAPSHOT_DIR.rglob("*.json"), key=lambda x: x.name)

    valid_snapshots = []

    for path in reversed(files):
        try:
            with open(path, "r") as f:
                snapshot = json.load(f)
            valid_snapshots.append(snapshot)
        except Exception as e:
            print(f"WARNING: Skipping invalid snapshot: {path.name} ({e})")
            continue

        if len(valid_snapshots) == 2:
            break

    if len(valid_snapshots) < 2:
        return None, None

    latest = valid_snapshots[0]
    previous = valid_snapshots[1]

    return previous, latest


# ==========================================
# BUILD THEME → CATEGORY MAP
# ==========================================

def build_theme_category_map(snapshot):

    theme_map = {}
    leading_themes = set()
    lagging_themes = set()

    for item in snapshot["leading_themes"]:
        theme_map[item["theme"]] = {
            "state": "Leading",
            "days": item.get("days", 1),
            "rank": item.get("rank"),
            "score": item.get("score"),
        }
        leading_themes.add(item["theme"])

    for item in snapshot["neutral_themes"]:
        theme_map[item["theme"]] = {
            "state": "Neutral",
            "days": item.get("days", 1),
            "rank": item.get("rank"),
            "score": item.get("score"),
        }

    for item in snapshot["lagging_themes"]:
        theme_map[item["theme"]] = {
            "state": "Lagging",
            "days": item.get("days", 1),
            "rank": item.get("rank"),
            "score": item.get("score"),
        }
        lagging_themes.add(item["theme"])

    return theme_map, leading_themes, lagging_themes


def classify_direction(previous_rank, latest_rank, previous_score, latest_score):

    strengthening_signals = 0
    weakening_signals = 0

    if previous_rank is not None and latest_rank is not None:
        if latest_rank < previous_rank:
            strengthening_signals += 1
        elif latest_rank > previous_rank:
            weakening_signals += 1

    if previous_score is not None and latest_score is not None:
        if latest_score > previous_score:
            strengthening_signals += 1
        elif latest_score < previous_score:
            weakening_signals += 1

    if strengthening_signals > weakening_signals:
        return "Strengthening"

    if weakening_signals > strengthening_signals:
        return "Weakening"

    return "Stable"


# ==========================================
# CALCULATE ROTATION DELTA
# ==========================================

def calculate_rotation_delta():

    previous, latest = load_last_two_snapshots()

    if previous is None:
        return None

    previous_map, previous_leading, previous_lagging = build_theme_category_map(previous)
    latest_map, latest_leading, latest_lagging = build_theme_category_map(latest)

    previous_themes = set(previous_map.keys())
    latest_themes = set(latest_map.keys())

    new_entries = list(latest_themes - previous_themes)

    exits = list(previous_themes - latest_themes)

    persistent_same_bucket = []
    rank_changes = []
    score_changes = []
    strengthening_themes = []
    weakening_themes = []

    for theme in sorted(previous_themes & latest_themes):
        previous_payload = previous_map.get(theme, {})
        latest_payload = latest_map.get(theme, {})

        previous_state = previous_payload.get("state")
        latest_state = latest_payload.get("state")

        if previous_state != latest_state:
            continue

        previous_rank = previous_payload.get("rank")
        latest_rank = latest_payload.get("rank")
        previous_score = previous_payload.get("score")
        latest_score = latest_payload.get("score")

        rank_change = None
        if previous_rank is not None and latest_rank is not None:
            rank_change = latest_rank - previous_rank

        score_change = None
        if previous_score is not None and latest_score is not None:
            score_change = round(latest_score - previous_score, 2)

        has_rank_change = rank_change not in (None, 0)
        has_score_change = score_change not in (None, 0)

        if not (has_rank_change or has_score_change):
            continue

        direction = classify_direction(
            previous_rank,
            latest_rank,
            previous_score,
            latest_score,
        )

        change_record = {
            "theme": theme,
            "bucket": latest_state,
            "previous_rank": previous_rank,
            "latest_rank": latest_rank,
            "rank_change": rank_change,
            "previous_score": previous_score,
            "latest_score": latest_score,
            "score_change": score_change,
            "direction": direction,
        }

        persistent_same_bucket.append(change_record)

        if has_rank_change:
            rank_changes.append(change_record)

        if has_score_change:
            score_changes.append(change_record)

        if direction == "Strengthening":
            strengthening_themes.append(change_record)
        elif direction == "Weakening":
            weakening_themes.append(change_record)

    persistent_leaders = [
        item for item in persistent_same_bucket
        if item["bucket"] == "Leading"
    ]

    persistent_laggards = [
        item for item in persistent_same_bucket
        if item["bucket"] == "Lagging"
    ]

    rotation_data = {

        "date": latest["date"],

        "compared_against": previous["date"],

        "new_entries": sorted(new_entries),

        "exits": sorted(exits),

        "entered_leading": sorted(latest_leading - previous_leading),

        "exited_leading": sorted(previous_leading - latest_leading),

        "entered_lagging": sorted(latest_lagging - previous_lagging),

        "exited_lagging": sorted(previous_lagging - latest_lagging),

        "persistent_same_bucket": persistent_same_bucket,

        "persistent_leaders": persistent_leaders,

        "persistent_laggards": persistent_laggards,

        "rank_changes": rank_changes,

        "score_changes": score_changes,

        "strengthening_themes": strengthening_themes,

        "weakening_themes": weakening_themes,

    }

    return rotation_data


# ==========================================
# SAVE ROTATION DELTA JSON
# ==========================================

def save_rotation_delta(rotation_data):

    if rotation_data is None:
        return

    target_dir = get_monthly_path(ROTATION_DIR, rotation_data['date'])
    filename = os.path.join(
        target_dir,
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

    print("\n========================================")
    print("STRUCTURAL ROTATION SUMMARY")
    print("========================================")
    print(f"Period : {rotation_data['compared_against']} -> {rotation_data['date']}")

    print("\nSUMMARY")
    print("----------------------------------------")
    print(f"New Themes       : {len(rotation_data['new_entries'])}")
    print(f"Exited Themes    : {len(rotation_data['exits'])}")
    print(f"Entered Leading  : {len(rotation_data['entered_leading'])}")
    print(f"Exited Leading   : {len(rotation_data['exited_leading'])}")
    print(f"Entered Lagging  : {len(rotation_data['entered_lagging'])}")
    print(f"Exited Lagging   : {len(rotation_data['exited_lagging'])}")

    print("\nRESULT")
    print("----------------------------------------")

    changes_found = False

    sections = [
        ("New Themes", rotation_data["new_entries"]),
        ("Exited Themes", rotation_data["exits"]),
        ("Promoted to Leading", rotation_data["entered_leading"]),
        ("Demoted from Leading", rotation_data["exited_leading"]),
        ("Dropped to Lagging", rotation_data["entered_lagging"]),
        ("Recovered from Lagging", rotation_data["exited_lagging"]),
    ]

    for title, items in sections:
        if items:
            changes_found = True
            print(f"\n{title}")
            for item in sorted(items):
                print(f"  • {item}")

    if not changes_found:
        print("✓ Market structure remained stable.")
    else:
        print("\n✓ Structural rotation detected.")