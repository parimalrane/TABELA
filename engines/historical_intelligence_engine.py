import json
import os


SNAPSHOT_DIR = "market_data/snapshots"


def load_snapshot_window(min_days=1, max_days=21):
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
        with open(path, "r") as f:
            snapshots.append(json.load(f))

    return snapshots


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

    if len(snapshots) < 2:
        print()
        print("INSUFFICIENT HISTORY")
    else:
        print()
        if len(snapshots) < min_days:
            print("PRELIMINARY SIGNALS")
            print()

    # -----------------------------
    # Structural Rotation
    # -----------------------------
    structural = []

    for c in emerging_candidates:
        if c["class_transitions"]:
            structural.append({
                **c,
                "direction": "Emerging"
            })

    for c in weakening_candidates:
        if c["class_transitions"]:
            structural.append({
                **c,
                "direction": "Weakening"
            })

    print("STRUCTURAL ROTATION")
    print("-" * 75)
    print(f"{'Theme':<35}{'Rank Chg':>10}{'Score Chg':>11}   Transition")
    print("-" * 75)

    if structural:

        structural.sort(
            key=lambda x: (
                0 if x["direction"] == "Emerging" else 1,
                emerging_priority(x["class_transitions"])
                if x["direction"] == "Emerging"
                else weakening_priority(x["class_transitions"])
            )
        )

        for c in structural:

            if c["direction"] == "Emerging":
                rank = f"{c['rank_improvement']:+}"
                score = f"{c['score_improvement']:+.2f}"
            else:
                rank = f"{-c['rank_deterioration']:+}"
                score = f"{-c['score_decline']:+.2f}"

            print(
                f"{c['theme']:<35}"
                f"{rank:>6}"
                f"{score:>10}   "
                f"{', '.join(c['class_transitions'])}"
            )
    else:
        print("- None")

    print()

    # -----------------------------
    # Strengthening Themes
    # -----------------------------
    print("STRENGTHENING THEMES")
    print("-" * 75)
    print(f"{'Theme':<35}{'↑ Rank':>8}{'↑ Score':>10}")
    print("-" * 75)

    strengthening = [c for c in emerging_candidates if not c["class_transitions"]]

    if strengthening:

        for c in strengthening:

            print(
                f"{c['theme']:<35}"
                f"{c['rank_improvement']:+6}"
                f"{c['score_improvement']:+10.2f}"
            )

    else:
        print("- None")

    print()

    # -----------------------------
    # Weakening Themes
    # -----------------------------
    print("WEAKENING THEMES")
    print("-" * 75)
    print(f"{'Theme':<35}{'↓ Rank':>8}{'↓ Score':>10}")
    print("-" * 75)

    weakening = [c for c in weakening_candidates if not c["class_transitions"]]

    if weakening:

        for c in weakening:

            print(
                f"{c['theme']:<35}"
                f"{-c['rank_deterioration']:+6}"
                f"{-c['score_decline']:+10.2f}"
            )

    else:
        print("- None")

    return {
        "window_days": len(snapshots),
        "theme_daily_series": theme_daily_series,
        "theme_daily_deltas": raw_deltas,
        "emerging_candidates": emerging_candidates,
        "weakening_candidates": weakening_candidates,
    }