from engines.historical_query_engine import load_history
from engines.historical_queries import HistoricalQueries
from datetime import datetime
history = load_history()
queries = HistoricalQueries(history)

SNAPSHOT_DIR = "market_data/snapshots"
ROTATION_DIR = "market_data/rotation_delta"



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

def compute_historical_intelligence(max_days=21):
    """
    Build historical intelligence.

    Data only.
    No printing.
    No presentation.
    """

    snapshot_datasets = queries.datasets("snapshot")

    snapshots = [
        dataset.data
        for dataset in snapshot_datasets
        if dataset.data is not None
    ][-max_days:]

    theme_daily_series = build_theme_daily_series(snapshots)
    raw_deltas = compute_theme_daily_deltas(theme_daily_series)

    latest_run = queries.latest_run()

    rotation_data = None
    rotation_date = None

    if latest_run is not None:

        rotation_dataset = queries.dataset(
            latest_run,
            "rotation_delta",
        )

        if (
            rotation_dataset is not None
            and rotation_dataset.data
        ):

            rotation_data = rotation_dataset.data
            rotation_date = rotation_data.get("date")

    theme_daily_deltas = {}

    for theme, points in theme_daily_series.items():

        ordered_points = sorted(
            points,
            key=lambda x: (
                x.get("date") is None,
                x.get("date"),
            ),
        )

        theme_daily_deltas[theme] = {
            "points": ordered_points,
            "deltas": raw_deltas.get(theme, []),
        }

    emerging_candidates = detect_emerging_from_history(
        theme_daily_deltas
    )

    weakening_candidates = detect_weakening_from_history(
        theme_daily_deltas
    )

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

                    state_map[item["theme"]] = {
                        "state": state_name,
                        "rank": item.get("rank"),
                        "score": item.get("score"),
                    }

            return state_map

        previous_map = build_state_map(previous_snapshot)
        latest_map = build_state_map(latest_snapshot)

        for theme in sorted(
            set(previous_map.keys()) &
            set(latest_map.keys())
        ):

            previous_state = previous_map[theme]["state"]
            latest_state = latest_map[theme]["state"]

            if previous_state == latest_state:
                continue

            previous_rank = previous_map[theme]["rank"]
            latest_rank = latest_map[theme]["rank"]

            previous_score = previous_map[theme]["score"]
            latest_score = latest_map[theme]["score"]

            rank_delta = None
            if (
                previous_rank is not None
                and latest_rank is not None
            ):
                rank_delta = latest_rank - previous_rank

            score_delta = None
            if (
                previous_score is not None
                and latest_score is not None
            ):
                score_delta = round(
                    latest_score - previous_score,
                    2,
                )

            structural.append(
                {
                    "theme": theme,
                    "rank_delta": rank_delta,
                    "score_delta": score_delta,
                    "transition": f"{previous_state} -> {latest_state}",
                }
            )

    # ------------------------------------------------------------------
    # Theme history
    # Raw historical observations only.
    # No calculations are performed here.
    # ------------------------------------------------------------------

    theme_history = {}

    for theme, points in theme_daily_series.items():
        theme_history[theme] = [
            {
                "date": p["date"],
                "rank": p["rank"],
                "score": p["score"],
                "classification": p["class"],
            }
            for p in points
        ]

    return {
        "window_days": len(snapshots),

        # Raw historical series
        "theme_history": theme_history,

        # Existing structures retained for backward compatibility
        "theme_daily_series": theme_daily_series,
        "theme_daily_deltas": raw_deltas,

        "emerging_candidates": emerging_candidates,
        "weakening_candidates": weakening_candidates,

        "daily_rotation_date": rotation_date,
        "daily_rotation_data": rotation_data,
    }

import pandas as pd

def build_theme_performance_table(theme_strength, max_days=63):
    """
    Build one normalized Theme Performance table.

    Read-only.
    Uses existing snapshot history and rotation data.
    """

    snapshot_datasets = queries.datasets("snapshot")

    snapshots = [
        dataset.data
        for dataset in snapshot_datasets
        if dataset.data is not None
    ][-max_days:]

    # -------------------------------------------------------
    # Historical score series
    # -------------------------------------------------------

    history = {}

    for snapshot in snapshots:

        for state in (
            "leading_themes",
            "neutral_themes",
            "lagging_themes",
        ):

            for item in snapshot.get(state, []):

                theme = item["theme"]

                history.setdefault(theme, []).append(
                    {
                        "date": snapshot["date"],
                        "rank": item["rank"],
                        "score": item["score"],
                    }
                )

    # -------------------------------------------------------
    # Structural transition (latest snapshot pair)
    # -------------------------------------------------------

    transition_lookup = {}

    if len(snapshots) >= 2:

        previous = snapshots[-2]
        latest = snapshots[-1]

        def build_state_map(snapshot):

            mapping = {}

            for key, state in [
                ("leading_themes", "Leading"),
                ("neutral_themes", "Neutral"),
                ("lagging_themes", "Lagging"),
            ]:

                for item in snapshot.get(key, []):

                    mapping[item["theme"]] = {
                        "state": state,
                        "rank": item.get("rank"),
                        "score": item.get("score"),
                    }

            return mapping

        previous_map = build_state_map(previous)
        latest_map = build_state_map(latest)

        for theme in set(previous_map) & set(latest_map):

            previous_state = previous_map[theme]["state"]
            latest_state = latest_map[theme]["state"]

            previous_rank = previous_map[theme]["rank"]
            latest_rank = latest_map[theme]["rank"]

            previous_score = previous_map[theme]["score"]
            latest_score = latest_map[theme]["score"]

            rank_delta = None
            if previous_rank is not None and latest_rank is not None:
                rank_delta = latest_rank - previous_rank

            score_delta = None
            if previous_score is not None and latest_score is not None:
                score_delta = round(
                    latest_score - previous_score,
                    2,
                )

            transition_lookup[theme] = {
                "transition": (
                    None
                    if previous_state == latest_state
                    else f"{previous_state} -> {latest_state}"
                ),
                "rank_delta": rank_delta,
                "score_delta": score_delta,
            }

    # -------------------------------------------------------
    # Final table
    # -------------------------------------------------------

    rows = []

    for _, current in (
        theme_strength
        .sort_values("Theme_Rank")
        .iterrows()
    ):

        theme = current["Theme"]

        points = sorted(
            history.get(theme, []),
            key=lambda x: x["date"],
        )

        current_rank = int(current["Theme_Rank"])
        current_score = float(current["ETF_RS_Raw"])

        d = w = m = q = None

        if len(points) >= 2:
            d = round(current_score - points[-2]["score"], 2)

        if len(points) >= 6:
            w = round(current_score - points[-6]["score"], 2)

        if len(points) >= 22:
            m = round(current_score - points[-22]["score"], 2)

        if len(points) >= 64:
            q = round(current_score - points[-64]["score"], 2)

        movement = transition_lookup.get(theme, {})

        rows.append(
            {
                "Rank": current_rank,
                "Theme": theme,
                "Strength": round(current_score, 2),
                "D": d,
                "W": w,
                "M": m,
                "Q": q,
                "Rank Δ": movement.get("rank_delta"),
                "Score Δ": movement.get("score_delta"),
                "Transition": movement.get("transition"),
            }
        )

    return pd.DataFrame(rows)[
        [
            "Rank",
            "Theme",
            "Strength",
            "D",
            "W",
            "M",
            "Q",
            "Rank Δ",
            "Score Δ",
            "Transition",
        ]
    ]
