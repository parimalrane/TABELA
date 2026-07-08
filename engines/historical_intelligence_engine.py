import json
import os
from datetime import datetime


SNAPSHOT_DIR = "market_data/snapshots"
ROTATION_DIR = "market_data/rotation_delta"


def load_snapshot_window(min_days=1, max_days=21):
    if not os.path.exists(SNAPSHOT_DIR):
        return []

    files = sorted([
        f for f in os.listdir(SNAPSHOT_DIR)
        if f.endswith(".json")
    ])

    if len(files) < min_days:
        return []

    selected_files = files[-max_days:]
    snapshots = []

    for filename in selected_files:
        path = os.path.join(SNAPSHOT_DIR, filename)
        try:
            with open(path, "r") as f:
                snapshots.append(json.load(f))
        except Exception as e:
            print(f"WARNING: Skipping invalid snapshot: {filename} ({e})")
            continue

    return snapshots


def load_latest_valid_rotation_delta():
    if not os.path.exists(ROTATION_DIR):
        return None, None

    files = sorted([
        f for f in os.listdir(ROTATION_DIR)
        if f.endswith("_rotation_delta.json")
    ])

    for filename in reversed(files):
        path = os.path.join(ROTATION_DIR, filename)
        try:
            with open(path, "r") as f:
                payload = json.load(f)

            if not isinstance(payload, dict):
                raise ValueError("rotation payload is not a JSON object")

            rotation_date = payload.get("date")
            if not rotation_date:
                rotation_date = filename.replace("_rotation_delta.json", "")

            return payload, rotation_date
        except Exception as e:
            print(f"WARNING: Skipping invalid rotation delta: {filename} ({e})")
            continue

    return None, None


def build_theme_daily_series(snapshots):
    series = {}

    for snapshot in snapshots:
        date = snapshot.get("date")

        for state_key, state_name in [
            ("leading_themes", "Leading"),
            ("neutral_themes", "Neutral"),
            ("lagging_themes", "Lagging"),
        ]:
            for item in snapshot.get(state_key, []):
                theme = item.get("theme")
                if theme is None:
                    continue

                if theme not in series:
                    series[theme] = []

                series[theme].append(
                    {
                        "date": date,
                        "rank": item.get("rank"),
                        "score": item.get("score"),
                        "class": state_name,
                    }
                )

    return series


def compute_theme_daily_deltas(theme_daily_series):
    deltas = {}

    for theme, points in theme_daily_series.items():
        ordered_points = sorted(points, key=lambda x: (x.get("date") is None, x.get("date")))
        theme_deltas = []

        for i in range(1, len(ordered_points)):
            prev_point = ordered_points[i - 1]
            curr_point = ordered_points[i]

            prev_rank = prev_point.get("rank")
            curr_rank = curr_point.get("rank")
            prev_score = prev_point.get("score")
            curr_score = curr_point.get("score")

            rank_delta = None
            if prev_rank is not None and curr_rank is not None:
                rank_delta = curr_rank - prev_rank

            score_delta = None
            if prev_score is not None and curr_score is not None:
                score_delta = curr_score - prev_score

            theme_deltas.append(
                {
                    "date": curr_point.get("date"),
                    "from_class": prev_point.get("class"),
                    "to_class": curr_point.get("class"),
                    "rank_delta": rank_delta,
                    "score_delta": score_delta,
                }
            )

        deltas[theme] = theme_deltas

    return deltas

def emerging_priority(transitions):
    if "Lagging -> Leading" in transitions:
        return 0
    if "Neutral -> Leading" in transitions:
        return 1
    if "Lagging -> Neutral" in transitions:
        return 2
    return 3


def weakening_priority(transitions):
    if "Leading -> Lagging" in transitions:
        return 0
    if "Leading -> Neutral" in transitions:
        return 1
    if "Neutral -> Lagging" in transitions:
        return 2
    return 3



def detect_emerging_from_history(theme_daily_deltas):
    emerging_candidates = []

    for theme, payload in theme_daily_deltas.items():
        deltas = payload.get("deltas", [])
        points = payload.get("points", [])

        if len(points) < 2:
            continue

        first_score = points[0].get("score")
        last_score = points[-1].get("score")

        first_rank = points[0].get("rank")
        last_rank = points[-1].get("rank")

        rank_improvement = None
        if first_rank is not None and last_rank is not None:
            rank_improvement = first_rank - last_rank

        score_improvement = None
        if first_score is not None and last_score is not None:
            score_improvement = round(last_score - first_score, 2)

        class_transitions = []
        for d in deltas:
            from_class = d.get("from_class")
            to_class = d.get("to_class")
            if (from_class == "Lagging" and to_class == "Neutral") or (
                from_class == "Neutral" and to_class == "Leading"
            ):
                class_transitions.append(f"{from_class} -> {to_class}")

        has_rank_improvement = rank_improvement is not None and rank_improvement > 0
        has_score_improvement = score_improvement is not None and score_improvement >= 2

        signal_strength = 0

        if has_rank_improvement:
            signal_strength += 1

        if has_score_improvement:
            signal_strength += 1

        if class_transitions:
            signal_strength += 2

        if signal_strength < 2:
            continue    
        
        current_class = points[-1].get("class")

        if current_class == "Lagging":
            continue

        emerging_candidates.append(
            {
                "theme": theme,
                "first_date": points[0].get("date"),
                "last_date": points[-1].get("date"),
                "first_rank": first_rank,
                "last_rank": last_rank,
                "first_score": first_score,
                "last_score": last_score,
                "rank_improvement": rank_improvement,
                "score_improvement": score_improvement,
                "class_transitions": class_transitions,
            }
        )

    emerging_candidates.sort(
        key=lambda x: (
            emerging_priority(x["class_transitions"]),
            -(x.get("rank_improvement") or 0),
            -(x.get("score_improvement") or 0),
            x["theme"],
        )
    )

    return emerging_candidates


def detect_weakening_from_history(theme_daily_deltas):
    weakening_candidates = []

    for theme, payload in theme_daily_deltas.items():
        deltas = payload.get("deltas", [])
        points = payload.get("points", [])

        if len(points) < 2:
            continue

        first_score = points[0].get("score")
        last_score = points[-1].get("score")

        first_rank = points[0].get("rank")
        last_rank = points[-1].get("rank")

        rank_deterioration = None
        if first_rank is not None and last_rank is not None:
            rank_deterioration = last_rank - first_rank

        score_decline = None
        if first_score is not None and last_score is not None:
            score_decline = round(first_score - last_score, 2)

        class_transitions = []
        for d in deltas:
            from_class = d.get("from_class")
            to_class = d.get("to_class")
            if (from_class == "Leading" and to_class == "Neutral") or (
                from_class == "Neutral" and to_class == "Lagging"
            ):
                class_transitions.append(f"{from_class} -> {to_class}")

        has_rank_deterioration = rank_deterioration is not None and rank_deterioration > 0
        has_score_decline = score_decline is not None and score_decline >= 2

        signal_strength = 0

        if has_rank_deterioration:
            signal_strength += 1

        if has_score_decline:
            signal_strength += 1

        if class_transitions:
            signal_strength += 2

        if signal_strength < 2:
            continue

        current_class = points[-1].get("class")

        if current_class == "Leading":
            continue

        weakening_candidates.append(
            {
                "theme": theme,
                "first_date": points[0].get("date"),
                "last_date": points[-1].get("date"),
                "first_rank": first_rank,
                "last_rank": last_rank,
                "first_score": first_score,
                "last_score": last_score,
                "rank_deterioration": rank_deterioration,
                "score_decline": score_decline,
                "class_transitions": class_transitions,
            }
        )

    weakening_candidates.sort(
        key=lambda x: (
            weakening_priority(x["class_transitions"]),
            -(x.get("rank_deterioration") or 0),
            -(x.get("score_decline") or 0),
            x["theme"],
        )
    )

    return weakening_candidates


def build_historical_intelligence_report(min_days=3, max_days=21):
    snapshots = load_snapshot_window(min_days=1, max_days=max_days)
    theme_daily_series = build_theme_daily_series(snapshots)
    raw_deltas = compute_theme_daily_deltas(theme_daily_series)
    rotation_data, rotation_date = load_latest_valid_rotation_delta()

    theme_daily_deltas = {}
    for theme, points in theme_daily_series.items():
        ordered_points = sorted(points, key=lambda x: (x.get("date") is None, x.get("date")))
        theme_daily_deltas[theme] = {
            "points": ordered_points,
            "deltas": raw_deltas.get(theme, []),
        }

    emerging_candidates = detect_emerging_from_history(theme_daily_deltas)
    weakening_candidates = detect_weakening_from_history(theme_daily_deltas)

    print("====================================")
    print("HISTORICAL INTELLIGENCE REPORT")
    print("====================================")

    today = datetime.today().strftime("%Y-%m-%d")

    print()
    print("DAILY ROTATION INTELLIGENCE")
    print("-" * 75)

    if rotation_data is None:
        print("Daily rotation data unavailable.")
    else:
        if rotation_date != today:
            print(f"NOTE: Using latest available rotation data ({rotation_date}).")

        rank_changes = rotation_data.get("rank_changes", [])
        score_changes = rotation_data.get("score_changes", [])
        strengthening_themes = rotation_data.get("strengthening_themes", [])
        weakening_themes = rotation_data.get("weakening_themes", [])

        top_strengthening = sorted(
            [
                x for x in strengthening_themes
                if isinstance(x.get("score_change"), (int, float))
            ],
            key=lambda x: abs(x.get("score_change")),
            reverse=True,
        )[:5]

        top_weakening = sorted(
            [
                x for x in weakening_themes
                if isinstance(x.get("score_change"), (int, float))
            ],
            key=lambda x: abs(x.get("score_change")),
            reverse=True,
        )[:5]

        print(f"Source Rotation Date: {rotation_date}")

        top_rank_movers = sorted(
            [
                x for x in rank_changes
                if isinstance(x.get("rank_change"), int)
            ],
            key=lambda x: abs(x.get("rank_change")),
            reverse=True,
        )[:10]

        print("\nTOP RANK MOVERS")
        print("-" * 75)
        if top_rank_movers:
            print(f"{'Theme':<35}Movement")
            for item in top_rank_movers:
                previous_rank = item.get("previous_rank")
                latest_rank = item.get("latest_rank")
                rank_change = item.get("rank_change")
                arrow = "↑" if rank_change < 0 else "↓"
                print(
                    f"{item.get('theme', '-'):<35}"
                    f"{arrow} {previous_rank} → {latest_rank}"
                )
        else:
            print("None")

        top_score_movers = sorted(
            [
                x for x in score_changes
                if isinstance(x.get("score_change"), (int, float))
            ],
            key=lambda x: abs(x.get("score_change")),
            reverse=True,
        )[:10]

        print("\nTOP SCORE MOVERS")
        print("-" * 75)
        if top_score_movers:
            print(f"{'Theme':<35}Score Change")
            for item in top_score_movers:
                delta = item.get("score_change")
                print(
                    f"{item.get('theme', '-'):<35}"
                    f"{delta:+.2f}"
                )
        else:
            print("None")

        print("\nSTRENGTHENING THEMES (TOP 5)")
        print("-" * 75)
        if top_strengthening:
            for item in top_strengthening:
                score_change = item.get("score_change")
                print(
                    f"{item.get('theme', '-'):<35}"
                    f"score {score_change:+.2f}"
                )
        else:
            print("None")

        print("\nWEAKENING THEMES (TOP 5)")
        print("-" * 75)
        if top_weakening:
            for item in top_weakening:
                score_change = item.get("score_change")
                print(
                    f"{item.get('theme', '-'):<35}"
                    f"score {score_change:+.2f}"
                )
        else:
            print("None")

    print()

    # -----------------------------
    # Structural Rotation (latest valid snapshot pair only)
    # -----------------------------
    structural = []

    if len(snapshots) >= 2:
        previous_snapshot = snapshots[-2]
        latest_snapshot = snapshots[-1]

        def build_state_map(snapshot):
            state_map = {}

            for state_key, state_name in [
                ("leading_themes", "Leading"),
                ("neutral_themes", "Neutral"),
                ("lagging_themes", "Lagging"),
            ]:
                for item in snapshot.get(state_key, []):
                    theme = item.get("theme")
                    if theme is None:
                        continue
                    state_map[theme] = {
                        "state": state_name,
                        "rank": item.get("rank"),
                        "score": item.get("score"),
                    }

            return state_map

        previous_map = build_state_map(previous_snapshot)
        latest_map = build_state_map(latest_snapshot)

        for theme in sorted(set(previous_map.keys()) & set(latest_map.keys())):
            previous_state = previous_map[theme].get("state")
            latest_state = latest_map[theme].get("state")

            if previous_state == latest_state:
                continue

            previous_rank = previous_map[theme].get("rank")
            latest_rank = latest_map[theme].get("rank")

            previous_score = previous_map[theme].get("score")
            latest_score = latest_map[theme].get("score")

            rank_delta = None
            if previous_rank is not None and latest_rank is not None:
                rank_delta = latest_rank - previous_rank

            score_delta = None
            if previous_score is not None and latest_score is not None:
                score_delta = round(latest_score - previous_score, 2)

            structural.append(
                {
                    "theme": theme,
                    "rank_delta": rank_delta,
                    "score_delta": score_delta,
                    "transition": f"{previous_state} -> {latest_state}",
                }
            )

    print("STRUCTURAL ROTATION")
    print("-" * 75)
    print(f"{'Theme':<35}{'Rank Chg':>10}{'Score Chg':>11}   Transition")
    print("-" * 75)

    if structural:
        for c in structural:
            rank = "n/a" if c["rank_delta"] is None else f"{c['rank_delta']:+}"
            score = "n/a" if c["score_delta"] is None else f"{c['score_delta']:+.2f}"

            print(
                f"{c['theme']:<35}"
                f"{rank:>6}"
                f"{score:>10}   "
                f"{c['transition']}"
            )
    else:
        print("No structural rotation detected.")

    print()
    print("MULTI-DAY INTELLIGENCE")
    print("-" * 75)
    if len(snapshots) < 20:
        print(f"Insufficient historical data ({len(snapshots)}/20 snapshots collected).")
    else:
        print("No multi-day intelligence available yet. More history required.")

    print()

    return {
        "window_days": len(snapshots),
        "theme_daily_series": theme_daily_series,
        "theme_daily_deltas": raw_deltas,
        "emerging_candidates": emerging_candidates,
        "weakening_candidates": weakening_candidates,
        "daily_rotation_date": rotation_date,
        "daily_rotation_data": rotation_data,
    }