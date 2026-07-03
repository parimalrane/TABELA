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
        has_score_improvement = score_improvement is not None and score_improvement > 0

        if not has_rank_improvement and not has_score_improvement and not class_transitions:
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
            x.get("last_rank") if x.get("last_rank") is not None else 10**9,
            -(x.get("rank_improvement") if x.get("rank_improvement") is not None else -10**9),
            -(x.get("score_improvement") if x.get("score_improvement") is not None else -10**9),
            x.get("theme", ""),
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
        has_score_decline = score_decline is not None and score_decline > 0

        if not has_rank_deterioration and not has_score_decline and not class_transitions:
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
            x.get("last_rank") if x.get("last_rank") is not None else 10**9,
            -(x.get("rank_deterioration") if x.get("rank_deterioration") is not None else -10**9),
            -(x.get("score_decline") if x.get("score_decline") is not None else -10**9),
            x.get("theme", ""),
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

        print("EMERGING THEMES")
        if emerging_candidates:
            for c in emerging_candidates:
                class_transition_text = ", ".join(c["class_transitions"]) if c["class_transitions"] else "None"
                print(
                    f"{c['theme']} | Rank Improvement {c['rank_improvement']} | "
                    f"Score Improvement {c['score_improvement']} | "
                    f"Class Transition {class_transition_text}"
                )
        else:
            print("- None")

        print()
        print("WEAKENING THEMES")
        if weakening_candidates:
            for c in weakening_candidates:
                class_transition_text = ", ".join(c["class_transitions"]) if c["class_transitions"] else "None"
                print(
                    f"{c['theme']} | Rank Deterioration {c['rank_deterioration']} | "
                    f"Score Decline {c['score_decline']} | "
                    f"Class Transition {class_transition_text}"
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