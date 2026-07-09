import json
import os
from typing import Dict, List, Optional

import pandas as pd


STOCK_HISTORY_DIR = "market_data/stock_universe"
SNAPSHOT_DIR = "market_data/snapshots"
ROTATION_DIR = "market_data/rotation_delta"


def _safe_float(value) -> Optional[float]:
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return None
    return float(numeric_value)


def _load_recent_json_payloads(directory: str, suffix: str, max_files: int = 21) -> List[dict]:
    if not os.path.exists(directory):
        return []

    files = sorted([f for f in os.listdir(directory) if f.endswith(suffix)])
    if not files:
        return []

    selected_files = files[-max_files:]
    payloads: List[dict] = []

    for filename in selected_files:
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, "r") as handle:
                payload = json.load(handle)
            payloads.append(payload)
        except Exception as error:
            print(f"WARNING: Skipping invalid JSON file: {filename} ({error})")

    return payloads


def _build_stock_history_index(max_days: int = 21) -> Dict[str, List[dict]]:
    history_payloads = _load_recent_json_payloads(
        directory=STOCK_HISTORY_DIR,
        suffix="_stock_history.json",
        max_files=max_days,
    )

    history_index: Dict[str, List[dict]] = {}

    for daily_payload in history_payloads:
        if not isinstance(daily_payload, list):
            continue

        for row in daily_payload:
            ticker = str(row.get("ticker", "")).strip().upper()
            if not ticker:
                continue

            history_index.setdefault(ticker, []).append(row)

    for ticker, records in history_index.items():
        history_index[ticker] = sorted(records, key=lambda x: str(x.get("scan_date", "")))

    return history_index


def _build_theme_snapshot_context(max_days: int = 21) -> Dict[str, dict]:
    snapshots = _load_recent_json_payloads(
        directory=SNAPSHOT_DIR,
        suffix="_market_snapshot.json",
        max_files=max_days,
    )

    theme_points: Dict[str, List[dict]] = {}

    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            continue

        snapshot_date = snapshot.get("date")

        for state_key, state_name in (
            ("leading_themes", "Leading"),
            ("neutral_themes", "Neutral"),
            ("lagging_themes", "Lagging"),
        ):
            for item in snapshot.get(state_key, []):
                theme = item.get("theme")
                if not theme:
                    continue

                theme_points.setdefault(theme, []).append(
                    {
                        "date": snapshot_date,
                        "class": state_name,
                        "rank": item.get("rank"),
                        "score": item.get("score"),
                    }
                )

    context: Dict[str, dict] = {}

    for theme, points in theme_points.items():
        ordered_points = sorted(points, key=lambda x: str(x.get("date", "")))

        lagging_streak = 0
        for point in reversed(ordered_points):
            if point.get("class") != "Lagging":
                break
            lagging_streak += 1

        weakening_transitions = 0
        for i in range(1, len(ordered_points)):
            previous_class = ordered_points[i - 1].get("class")
            current_class = ordered_points[i].get("class")
            if (
                previous_class == "Leading" and current_class == "Neutral"
            ) or (
                previous_class == "Neutral" and current_class == "Lagging"
            ):
                weakening_transitions += 1

        context[theme] = {
            "lagging_streak": lagging_streak,
            "weakening_transitions": weakening_transitions,
            "history_points": len(ordered_points),
        }

    return context


def _load_latest_rotation_context() -> dict:
    payloads = _load_recent_json_payloads(
        directory=ROTATION_DIR,
        suffix="_rotation_delta.json",
        max_files=3,
    )

    for payload in reversed(payloads):
        if not isinstance(payload, dict):
            continue

        weakening_themes = {
            item.get("theme")
            for item in payload.get("weakening_themes", [])
            if item.get("theme")
        }

        entered_lagging = set(payload.get("entered_lagging", []))
        exited_leading = set(payload.get("exited_leading", []))

        return {
            "weakening_themes": weakening_themes,
            "entered_lagging": entered_lagging,
            "exited_leading": exited_leading,
        }

    return {
        "weakening_themes": set(),
        "entered_lagging": set(),
        "exited_leading": set(),
    }


def _consecutive_deterioration_days(series: List[Optional[float]]) -> int:
    valid_values = [value for value in series if value is not None]
    if len(valid_values) < 2:
        return 0

    streak = 0
    for i in range(len(valid_values) - 1, 0, -1):
        latest = valid_values[i]
        previous = valid_values[i - 1]
        if latest < previous:
            streak += 1
        else:
            break

    return streak


def _deterioration_days_in_window(
    series: List[Optional[float]],
    current_value: Optional[float],
    window_days: int = 5,
) -> int:
    valid_values = [value for value in series if value is not None]
    if current_value is None:
        return 0

    full_series = valid_values + [current_value]
    if len(full_series) < 2:
        return 0

    recent_series = full_series[-(window_days + 1):]
    declines = 0
    for i in range(1, len(recent_series)):
        if recent_series[i] < recent_series[i - 1]:
            declines += 1
    return declines


def _recent_baseline_deterioration(
    series: List[Optional[float]],
    current_value: Optional[float],
    lookback_days: int = 5,
) -> Optional[float]:
    valid_values = [value for value in series if value is not None]
    if not valid_values or current_value is None:
        return None
    recent_values = valid_values[-lookback_days:]
    recent_baseline = float(pd.Series(recent_values).median())
    return round(recent_baseline - current_value, 2)


def _days_since_leadership_loss(
    series: List[Optional[float]],
    current_value: Optional[float],
    threshold: float = 80.0,
) -> Optional[int]:
    valid_values = [value for value in series if value is not None]
    if current_value is None:
        return None

    full_series = valid_values + [current_value]
    if len(full_series) < 2:
        return None

    if current_value >= threshold:
        return None

    if max(full_series[:-1]) < threshold:
        return None

    days_ago = 0
    for i in range(len(full_series) - 1, 0, -1):
        current_point = full_series[i]
        previous_point = full_series[i - 1]
        if previous_point >= threshold and current_point < threshold:
            return days_ago
        days_ago += 1

    return None


def _trend_metrics(
    history_records: List[dict],
    current_rs: Optional[float],
    current_composite: Optional[float],
) -> dict:
    rs_series: List[Optional[float]] = [
        _safe_float(record.get("rs_rating")) for record in history_records
    ]

    # Historical composite score support is forward-compatible.
    # Existing files may not include this yet, so we gracefully degrade.
    composite_series: List[Optional[float]] = [
        _safe_float(record.get("composite_score")) for record in history_records
    ]

    previous_rs = rs_series[-1] if rs_series else None
    previous_composite = composite_series[-1] if composite_series else None

    rs_drop_1d = None
    if previous_rs is not None and current_rs is not None:
        rs_drop_1d = round(previous_rs - current_rs, 2)

    composite_drop_1d = None
    if previous_composite is not None and current_composite is not None:
        composite_drop_1d = round(previous_composite - current_composite, 2)

    rs_drop_recent = _recent_baseline_deterioration(rs_series, current_rs, lookback_days=5)
    composite_drop_recent = _recent_baseline_deterioration(
        composite_series,
        current_composite,
        lookback_days=5,
    )

    rs_persistence_days = _consecutive_deterioration_days(rs_series + [current_rs])
    composite_persistence_days = _consecutive_deterioration_days(composite_series + [current_composite])
    rs_down_days_5d = _deterioration_days_in_window(rs_series, current_rs, window_days=5)
    composite_down_days_5d = _deterioration_days_in_window(
        composite_series,
        current_composite,
        window_days=5,
    )

    leadership_loss_days = _days_since_leadership_loss(rs_series, current_rs, threshold=80.0)

    return {
        "history_days": len(history_records),
        "rs_drop_1d": rs_drop_1d,
        "composite_drop_1d": composite_drop_1d,
        "rs_drop_recent": rs_drop_recent,
        "composite_drop_recent": composite_drop_recent,
        "rs_persistence_days": rs_persistence_days,
        "composite_persistence_days": composite_persistence_days,
        "rs_down_days_5d": rs_down_days_5d,
        "composite_down_days_5d": composite_down_days_5d,
        "leadership_loss_days": leadership_loss_days,
    }


def _theme_context_reasons(
    mapped_theme: str,
    theme_class: str,
    snapshot_context: Dict[str, dict],
    rotation_context: dict,
) -> List[str]:
    reasons: List[str] = []

    theme_snapshot = snapshot_context.get(mapped_theme, {})
    lagging_streak = int(theme_snapshot.get("lagging_streak", 0) or 0)
    weakening_transitions = int(theme_snapshot.get("weakening_transitions", 0) or 0)

    if theme_class == "Lagging":
        reasons.append("theme lagging")

    if mapped_theme in rotation_context.get("entered_lagging", set()):
        reasons.append("theme entered lagging")

    if mapped_theme in rotation_context.get("exited_leading", set()):
        reasons.append("theme exited leading")

    if mapped_theme in rotation_context.get("weakening_themes", set()):
        reasons.append("daily rotation weakening")

    if lagging_streak >= 3:
        reasons.append(f"theme lagging for {lagging_streak} days")

    if weakening_transitions >= 2:
        reasons.append(f"multi-day weakening x{weakening_transitions}")

    return reasons


def _primary_evidence(
    trend_metrics: dict,
    current_rs: Optional[float],
    current_composite: Optional[float],
    rs_universe_median: Optional[float],
    composite_universe_median: Optional[float],
) -> dict:
    reasons: List[str] = []

    history_days = int(trend_metrics.get("history_days", 0) or 0)
    rs_drop_1d = trend_metrics.get("rs_drop_1d")
    composite_drop_1d = trend_metrics.get("composite_drop_1d")
    rs_drop_recent = trend_metrics.get("rs_drop_recent")
    composite_drop_recent = trend_metrics.get("composite_drop_recent")
    rs_persistence_days = int(trend_metrics.get("rs_persistence_days", 0) or 0)
    composite_persistence_days = int(trend_metrics.get("composite_persistence_days", 0) or 0)
    rs_down_days_5d = int(trend_metrics.get("rs_down_days_5d", 0) or 0)
    composite_down_days_5d = int(trend_metrics.get("composite_down_days_5d", 0) or 0)
    leadership_loss_days = trend_metrics.get("leadership_loss_days")

    rs_deterioration = False
    composite_deterioration = False
    historical_signal = False
    leadership_signal = False
    fallback_signal = False

    if rs_drop_1d is not None:
        if rs_drop_1d > 0:
            rs_deterioration = True
            reasons.append(f"RS down {rs_drop_1d:.0f} vs prior day")

    if rs_drop_recent is not None:
        if rs_drop_recent > 0:
            rs_deterioration = True
            lookback = min(max(history_days, 1), 5)
            reasons.append(f"RS below recent {lookback}d baseline by {rs_drop_recent:.0f}")

    if composite_drop_1d is not None:
        if composite_drop_1d > 0:
            composite_deterioration = True
            reasons.append(f"Composite down {composite_drop_1d:.1f} vs prior day")

    if composite_drop_recent is not None:
        if composite_drop_recent > 0:
            composite_deterioration = True
            lookback = min(max(history_days, 1), 5)
            reasons.append(f"Composite below recent {lookback}d baseline by {composite_drop_recent:.1f}")

    if rs_persistence_days >= 2:
        rs_deterioration = True
        historical_signal = True
        reasons.append(f"RS deteriorating for {rs_persistence_days} trading days")

    if rs_down_days_5d >= 2 and rs_drop_recent is not None and rs_drop_recent >= 10:
        rs_deterioration = True
        historical_signal = True
        reasons.append(f"RS deteriorated on {rs_down_days_5d} of last 5 days")

    if composite_persistence_days >= 2:
        composite_deterioration = True
        historical_signal = True
        reasons.append(f"Composite deteriorating for {composite_persistence_days} trading days")

    if (
        composite_down_days_5d >= 2
        and composite_drop_recent is not None
        and composite_drop_recent >= 5
    ):
        composite_deterioration = True
        historical_signal = True
        reasons.append(f"Composite deteriorated on {composite_down_days_5d} of last 5 days")

    if leadership_loss_days is not None:
        leadership_signal = True
        day_label = "day" if leadership_loss_days == 1 else "days"
        reasons.append(f"Lost institutional leadership {leadership_loss_days} {day_label} ago")

    if rs_persistence_days >= 2 or composite_persistence_days >= 2:
        historical_signal = True
        reasons.append("Multi-day deterioration confirmed")

    if history_days == 0:
        if (
            current_rs is not None
            and current_composite is not None
            and rs_universe_median is not None
            and composite_universe_median is not None
            and current_rs < rs_universe_median
            and current_composite < composite_universe_median
        ):
            fallback_signal = True
            reasons.append("History unavailable; RS and Composite below universe median")

    return {
        "history_days": history_days,
        "rs_deterioration": rs_deterioration,
        "composite_deterioration": composite_deterioration,
        "historical_signal": historical_signal,
        "leadership_signal": leadership_signal,
        "fallback_signal": fallback_signal,
        "rs_persistence_days": rs_persistence_days,
        "composite_persistence_days": composite_persistence_days,
        "rs_down_days_5d": rs_down_days_5d,
        "composite_down_days_5d": composite_down_days_5d,
        "rs_drop_recent": rs_drop_recent,
        "composite_drop_recent": composite_drop_recent,
        "leadership_loss_days": leadership_loss_days,
        "reasons": reasons,
    }


def _is_distribution_candidate(evidence: dict) -> bool:
    multi_day_confirmed = bool(evidence.get("historical_signal"))
    dual_deterioration = bool(
        evidence.get("rs_deterioration") and evidence.get("composite_deterioration")
    )
    return bool(
        multi_day_confirmed
        or dual_deterioration
        or evidence.get("fallback_signal")
    )


def build_distribution_watchlist(stocks: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    if stocks is None or stocks.empty:
        return pd.DataFrame(columns=[
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "RS_Rating",
            "Composite_Score",
            "Distribution_Reasons",
        ])

    stock_history_index = _build_stock_history_index(max_days=21)
    snapshot_context = _build_theme_snapshot_context(max_days=21)
    rotation_context = _load_latest_rotation_context()

    rs_universe_median = _safe_float(stocks["RS_Rating"].median()) if "RS_Rating" in stocks.columns else None
    composite_universe_median = (
        _safe_float(stocks["Composite_Score"].median())
        if "Composite_Score" in stocks.columns
        else None
    )

    candidates = []

    for _, row in stocks.iterrows():
        ticker = str(row.get("Ticker", "")).strip().upper()
        if not ticker:
            continue

        mapped_theme = row.get("Mapped_Theme", "Unknown")
        theme_class = row.get("Theme_Class", "Unknown")

        history_records = stock_history_index.get(ticker, [])

        trend_metrics = _trend_metrics(
            history_records=history_records,
            current_rs=_safe_float(row.get("RS_Rating")),
            current_composite=_safe_float(row.get("Composite_Score")),
        )

        evidence = _primary_evidence(
            trend_metrics=trend_metrics,
            current_rs=_safe_float(row.get("RS_Rating")),
            current_composite=_safe_float(row.get("Composite_Score")),
            rs_universe_median=rs_universe_median,
            composite_universe_median=composite_universe_median,
        )
        if not _is_distribution_candidate(evidence):
            continue

        theme_reasons = _theme_context_reasons(
            mapped_theme=mapped_theme,
            theme_class=theme_class,
            snapshot_context=snapshot_context,
            rotation_context=rotation_context,
        )

        row_copy = row.copy()
        all_reasons = evidence["reasons"] + theme_reasons
        row_copy["Distribution_Reasons"] = "; ".join(all_reasons[:5]) if all_reasons else "distribution evidence detected"
        row_copy["_Sort_RS_Persistence"] = int(evidence.get("rs_persistence_days", 0) or 0)
        row_copy["_Sort_Composite_Persistence"] = int(evidence.get("composite_persistence_days", 0) or 0)
        row_copy["_Sort_RS_Drop"] = _safe_float(evidence.get("rs_drop_recent")) or 0.0
        row_copy["_Sort_Composite_Drop"] = _safe_float(evidence.get("composite_drop_recent")) or 0.0
        row_copy["_Sort_Leadership_Loss_Days"] = int(evidence.get("leadership_loss_days", 9999) or 9999)
        candidates.append(row_copy)

    if not candidates:
        return pd.DataFrame(columns=[
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "RS_Rating",
            "Composite_Score",
            "Distribution_Reasons",
        ])

    distribution_watchlist = pd.DataFrame(candidates)
    distribution_watchlist = distribution_watchlist.sort_values(
        by=[
            "_Sort_RS_Persistence",
            "_Sort_Composite_Persistence",
            "_Sort_RS_Drop",
            "_Sort_Composite_Drop",
            "_Sort_Leadership_Loss_Days",
            "RS_Rating",
        ],
        ascending=[False, False, False, False, True, False],
    )
    distribution_watchlist = distribution_watchlist.drop(
        columns=[
            "_Sort_RS_Persistence",
            "_Sort_Composite_Persistence",
            "_Sort_RS_Drop",
            "_Sort_Composite_Drop",
            "_Sort_Leadership_Loss_Days",
        ],
        errors="ignore",
    )
    return distribution_watchlist.head(top_n)
