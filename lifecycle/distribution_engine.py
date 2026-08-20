import json
import os
from typing import Dict, List, Optional

import pandas as pd

from config.config import DISTRIBUTION_ENGINE_CONFIG


STOCK_HISTORY_DIR = "market_data/stock_universe"
SNAPSHOT_DIR = "market_data/snapshots"
ROTATION_DIR = "market_data/rotation_delta"
DISTRIBUTION_CFG = DISTRIBUTION_ENGINE_CONFIG


def _safe_float(value) -> Optional[float]:
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return None
    return float(numeric_value)


def _format_drop_token(prefix: str, value: Optional[float], decimals: int, min_abs: float) -> Optional[str]:
    if value is None:
        return None
    if abs(value) < min_abs:
        return None
    return f"{prefix}:-{abs(value):.{decimals}f}"


def _ordered_reason_tokens(tokens: List[str]) -> List[str]:
    ordered_groups = [
        "RS:",
        "Leader:",
        "Hist:",
        "Comp:",
        "Rot:",
        "Theme:",
    ]
    grouped: List[str] = []
    for prefix in ordered_groups:
        grouped.extend([token for token in tokens if token.startswith(prefix)])
    grouped.extend([token for token in tokens if token not in grouped])
    return grouped


from pathlib import Path

def _load_recent_json_payloads(directory: str, suffix: str, max_files: int) -> List[dict]:
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    files = sorted(dir_path.rglob(f"*{suffix}"), key=lambda x: x.name)
    if not files:
        return []

    selected_files = files[-max_files:]
    payloads: List[dict] = []

    for file_path in selected_files:
        try:
            with open(file_path, "r") as handle:
                payload = json.load(handle)
            payloads.append(payload)
        except Exception as error:
            print(f"WARNING: Skipping invalid JSON file: {file_path.name} ({error})")

    return payloads


def _build_stock_history_index(max_days: int) -> Dict[str, List[dict]]:
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


def _build_theme_snapshot_context(max_days: int) -> Dict[str, dict]:
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


def _load_latest_rotation_context(max_files: int) -> dict:
    payloads = _load_recent_json_payloads(
        directory=ROTATION_DIR,
        suffix="_rotation_delta.json",
        max_files=max_files,
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
    window_days: int,
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
    lookback_days: int,
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
    threshold: float,
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
    config: dict,
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

    rs_drop_recent = _recent_baseline_deterioration(
        rs_series,
        current_rs,
        lookback_days=int(config["RECENT_BASELINE_LOOKBACK_DAYS"]),
    )
    composite_drop_recent = _recent_baseline_deterioration(
        composite_series,
        current_composite,
        lookback_days=int(config["RECENT_BASELINE_LOOKBACK_DAYS"]),
    )

    rs_persistence_days = _consecutive_deterioration_days(rs_series + [current_rs])
    composite_persistence_days = _consecutive_deterioration_days(composite_series + [current_composite])
    rs_down_days_5d = _deterioration_days_in_window(
        rs_series,
        current_rs,
        window_days=int(config["DOWNTREND_WINDOW_DAYS"]),
    )
    composite_down_days_5d = _deterioration_days_in_window(
        composite_series,
        current_composite,
        window_days=int(config["DOWNTREND_WINDOW_DAYS"]),
    )

    leadership_loss_days = _days_since_leadership_loss(
        rs_series,
        current_rs,
        threshold=float(config["LEADERSHIP_RS_THRESHOLD"]),
    )

    return {
        "history_days": len(history_records),
        "composite_history_points": len([value for value in composite_series if value is not None]),
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
    config: dict,
) -> List[str]:
    reasons: List[str] = []

    theme_snapshot = snapshot_context.get(mapped_theme, {})
    lagging_streak = int(theme_snapshot.get("lagging_streak", 0) or 0)
    weakening_transitions = int(theme_snapshot.get("weakening_transitions", 0) or 0)

    if mapped_theme in rotation_context.get("weakening_themes", set()):
        reasons.append("Rot:Weak")

    if theme_class == "Lagging":
        reasons.append("Theme:Lag")

    if mapped_theme in rotation_context.get("entered_lagging", set()):
        reasons.append("Theme:EnterLag")

    if mapped_theme in rotation_context.get("exited_leading", set()):
        reasons.append("Theme:ExitLead")

    if lagging_streak >= int(config["MIN_THEME_LAGGING_STREAK_DAYS"]):
        reasons.append(f"Theme:Lag{lagging_streak}d")

    if weakening_transitions >= int(config["MIN_THEME_WEAKENING_TRANSITIONS"]):
        reasons.append(f"Theme:Weakx{weakening_transitions}")

    return reasons


def _primary_evidence(
    trend_metrics: dict,
    current_rs: Optional[float],
    current_composite: Optional[float],
    rs_universe_median: Optional[float],
    composite_universe_median: Optional[float],
    config: dict,
) -> dict:
    reasons: List[str] = []
    min_abs_delta = float(config["EVIDENCE_MIN_ABS_DELTA"])

    history_days = int(trend_metrics.get("history_days", 0) or 0)
    composite_history_points = int(trend_metrics.get("composite_history_points", 0) or 0)
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
    composite_confirmation = False
    history_confirmed = False

    if rs_drop_1d is not None:
        if rs_drop_1d > float(config["MIN_RS_DROP_1D"]):
            rs_deterioration = True
            rs_1d_token = _format_drop_token("RS", rs_drop_1d, 0, min_abs_delta)
            if rs_1d_token:
                reasons.append(f"{rs_1d_token}(1d)")

    if rs_drop_recent is not None:
        if rs_drop_recent > float(config["MIN_RS_DROP_RECENT"]):
            rs_deterioration = True
            rs_recent_token = _format_drop_token("RS", rs_drop_recent, 0, min_abs_delta)
            if rs_recent_token:
                reasons.append(rs_recent_token)

    if composite_drop_1d is not None:
        if composite_drop_1d > float(config["MIN_COMPOSITE_DROP_1D"]):
            composite_deterioration = True
            comp_1d_token = _format_drop_token("Comp", composite_drop_1d, 1, min_abs_delta)
            if comp_1d_token:
                reasons.append(f"{comp_1d_token}(1d)")

    if composite_drop_recent is not None:
        if composite_drop_recent > float(config["MIN_COMPOSITE_DROP_RECENT"]):
            composite_deterioration = True
            comp_recent_token = _format_drop_token("Comp", composite_drop_recent, 1, min_abs_delta)
            if comp_recent_token:
                reasons.append(comp_recent_token)

    if (
        bool(config["USE_COMPOSITE_MEDIAN_CONFIRMATION_WHEN_HISTORY_SPARSE"])
        and composite_history_points <= int(config["SPARSE_COMPOSITE_HISTORY_MAX_POINTS"])
        and current_composite is not None
        and composite_universe_median is not None
        and (composite_universe_median - current_composite)
        >= float(config["MIN_COMPOSITE_MEDIAN_CONFIRMATION_GAP"])
    ):
        composite_confirmation = True
        reasons.append("Comp<Med")

    if rs_persistence_days >= int(config["MIN_RS_PERSISTENCE_DAYS"]):
        rs_deterioration = True
        history_confirmed = True
        reasons.append(f"RS:{rs_persistence_days}d↓")

    if (
        rs_down_days_5d >= int(config["MIN_RS_DOWN_DAYS_IN_WINDOW"])
        and rs_drop_recent is not None
        and rs_drop_recent >= float(config["MIN_RS_DROP_RECENT_FOR_DOWN_DAYS"])
    ):
        rs_deterioration = True
        history_confirmed = True
        reasons.append(
            f"RS:{rs_down_days_5d}/{int(config['DOWNTREND_WINDOW_DAYS'])}↓"
        )

    if composite_persistence_days >= int(config["MIN_COMPOSITE_PERSISTENCE_DAYS"]):
        composite_deterioration = True
        composite_confirmation = True
        history_confirmed = True
        reasons.append(f"Comp:{composite_persistence_days}d↓")

    if (
        composite_down_days_5d >= int(config["MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW"])
        and composite_drop_recent is not None
        and composite_drop_recent >= float(config["MIN_COMPOSITE_DROP_RECENT_FOR_DOWN_DAYS"])
    ):
        composite_deterioration = True
        composite_confirmation = True
        history_confirmed = True
        reasons.append(
            f"Comp:{composite_down_days_5d}/{int(config['DOWNTREND_WINDOW_DAYS'])}↓"
        )

    if leadership_loss_days is not None:
        leadership_signal = True
        reasons.append(f"Leader:-{leadership_loss_days}d")
        if (
            bool(config["USE_LEADERSHIP_AS_HISTORY_CONFIRMATION"])
            and rs_drop_recent is not None
            and rs_drop_recent >= float(config["MIN_RS_DROP_RECENT_FOR_LEADERSHIP_CONFIRMATION"])
        ):
            history_confirmed = True

    if history_confirmed:
        historical_signal = True
        reasons.append("Hist:Confirm")

    if composite_deterioration:
        composite_confirmation = True

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
            reasons.append("Hist:Sparse")
            reasons.append("RS<Med")
            reasons.append("Comp<Med")

    return {
        "history_days": history_days,
        "rs_deterioration": rs_deterioration,
        "composite_deterioration": composite_deterioration,
        "historical_signal": historical_signal,
        "leadership_signal": leadership_signal,
        "composite_confirmation": composite_confirmation,
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
    rs_trigger = bool(evidence.get("rs_deterioration"))
    composite_confirmation = bool(evidence.get("composite_confirmation"))
    history_confirmed = bool(evidence.get("historical_signal"))
    return bool(
        (rs_trigger and composite_confirmation and history_confirmed)
        or evidence.get("fallback_signal")
    )


def build_distribution_watchlist(
    observation_candidates: pd.DataFrame,
    top_n: Optional[int] = None,
) -> pd.DataFrame:

    config = DISTRIBUTION_CFG
    effective_top_n = int(top_n or config.get("DISTRIBUTION_MAX_CAP", config.get("DEFAULT_TOP_N", 15)))
    if observation_candidates is None or observation_candidates.empty:
        return pd.DataFrame(columns=[
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "RS_Rating",
            "Composite_Score",
            "Distribution_Reasons",
        ])

    stock_history_index = _build_stock_history_index(max_days=int(config["MAX_HISTORY_DAYS"]))
    snapshot_context = _build_theme_snapshot_context(max_days=int(config["SNAPSHOT_MAX_DAYS"]))
    rotation_context = _load_latest_rotation_context(max_files=int(config["ROTATION_MAX_FILES"]))

    rs_universe_median = (
    _safe_float(observation_candidates["RS_Rating"].median())
    if "RS_Rating" in observation_candidates.columns
    else None
)
    composite_universe_median = (
        _safe_float(observation_candidates["Composite_Score"].median())
        if "Composite_Score" in observation_candidates.columns
        else None
    )

    candidates = []

    for _, row in observation_candidates.iterrows():
        ticker = str(row.get("Ticker", "")).strip().upper()
        if not ticker:
            continue

        mapped_theme = row.get("Mapped_Theme", "Unknown")
        theme_class = row.get("Theme_Class", "Unknown")
        rs_rating = _safe_float(row.get("RS_Rating")) or 0.0

        # Protect hot sectors (Rule 2)
        if theme_class in ["Leading", "Unclassified Leader"]:
            continue

        # Drop dead short candidates (Rule 3 Trapdoor)
        dist_min_rs = float(config.get("DISTRIBUTION_MIN_RS", 40))
        if rs_rating < dist_min_rs:
            continue

        history_records = stock_history_index.get(ticker, [])

        trend_metrics = _trend_metrics(
            history_records=history_records,
            current_rs=_safe_float(row.get("RS_Rating")),
            current_composite=_safe_float(row.get("Composite_Score")),
            config=config,
        )

        evidence = _primary_evidence(
            trend_metrics=trend_metrics,
            current_rs=_safe_float(row.get("RS_Rating")),
            current_composite=_safe_float(row.get("Composite_Score")),
            rs_universe_median=rs_universe_median,
            composite_universe_median=composite_universe_median,
            config=config,
        )
        if not _is_distribution_candidate(evidence):
            continue

        theme_reasons = _theme_context_reasons(
            mapped_theme=mapped_theme,
            theme_class=theme_class,
            snapshot_context=snapshot_context,
            rotation_context=rotation_context,
            config=config,
        )

        row_copy = row.copy()
        all_reasons = evidence["reasons"] + theme_reasons
        ordered_reasons = _ordered_reason_tokens(all_reasons)
        row_copy["Distribution_Reasons"] = " | ".join(
            ordered_reasons[: int(config["MAX_REASON_TOKENS"])]
        ) if all_reasons else "N/A"

        # Expose underlying formatted metrics for presentation custom columns
        rs_delta_val = "-"
        if evidence.get("rs_drop_recent") is not None and evidence.get("rs_drop_recent") >= float(config["MIN_RS_DROP_RECENT"]):
            rs_delta_val = f"-{int(round(evidence.get('rs_drop_recent')))}"
        elif trend_metrics.get("rs_drop_1d") is not None and trend_metrics.get("rs_drop_1d") >= float(config["MIN_RS_DROP_1D"]):
            rs_delta_val = f"-{int(round(trend_metrics.get('rs_drop_1d')))}(1d)"
        row_copy["RS_Delta_Val"] = rs_delta_val

        rs_trend_parts = []
        if evidence.get("rs_persistence_days", 0) >= int(config["MIN_RS_PERSISTENCE_DAYS"]):
            rs_trend_parts.append(f"{evidence['rs_persistence_days']}d\u2193")
        if (
            evidence.get("rs_down_days_5d", 0) >= int(config["MIN_RS_DOWN_DAYS_IN_WINDOW"])
            and evidence.get("rs_drop_recent") is not None
            and evidence.get("rs_drop_recent") >= float(config["MIN_RS_DROP_RECENT_FOR_DOWN_DAYS"])
        ):
            rs_trend_parts.append(f"{evidence['rs_down_days_5d']}/{int(config['DOWNTREND_WINDOW_DAYS'])}\u2193")
        row_copy["RS_Trend_Val"] = ", ".join(rs_trend_parts) if rs_trend_parts else "-"

        row_copy["Leadership_Loss_Val"] = f"-{evidence['leadership_loss_days']}d" if evidence.get("leadership_loss_days") is not None else "-"

        history_val = "-"
        if evidence.get("historical_signal"):
            history_val = "Confirm"
        elif evidence.get("fallback_signal"):
            history_val = "Sparse"
        row_copy["History_Val"] = history_val

        comp_delta_val = "-"
        if evidence.get("composite_drop_recent") is not None and evidence.get("composite_drop_recent") >= float(config["MIN_COMPOSITE_DROP_RECENT"]):
            comp_delta_val = f"-{evidence.get('composite_drop_recent'):.1f}"
        elif trend_metrics.get("composite_drop_1d") is not None and trend_metrics.get("composite_drop_1d") >= float(config["MIN_COMPOSITE_DROP_1D"]):
            comp_delta_val = f"-{trend_metrics.get('composite_drop_1d'):.1f}(1d)"
        row_copy["Composite_Delta_Val"] = comp_delta_val

        comp_trend_parts = []
        if evidence.get("composite_persistence_days", 0) >= int(config["MIN_COMPOSITE_PERSISTENCE_DAYS"]):
            comp_trend_parts.append(f"{evidence['composite_persistence_days']}d\u2193")
        if (
            evidence.get("composite_down_days_5d", 0) >= int(config["MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW"])
            and evidence.get("composite_drop_recent") is not None
            and evidence.get("composite_drop_recent") >= float(config["MIN_COMPOSITE_DROP_RECENT_FOR_DOWN_DAYS"])
        ):
            comp_trend_parts.append(f"{evidence['composite_down_days_5d']}/{int(config['DOWNTREND_WINDOW_DAYS'])}\u2193")
        if evidence.get("composite_confirmation") and not (
            evidence.get("composite_drop_recent") is not None and evidence.get("composite_drop_recent") >= float(config["MIN_COMPOSITE_DROP_RECENT"])
        ) and not (
            trend_metrics.get("composite_drop_1d") is not None and trend_metrics.get("composite_drop_1d") >= float(config["MIN_COMPOSITE_DROP_1D"])
        ) and not (
            evidence.get("composite_persistence_days", 0) >= int(config["MIN_COMPOSITE_PERSISTENCE_DAYS"])
        ) and not (
            evidence.get("composite_down_days_5d", 0) >= int(config["MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW"])
        ):
            if (
                bool(config["USE_COMPOSITE_MEDIAN_CONFIRMATION_WHEN_HISTORY_SPARSE"])
                and trend_metrics.get("composite_history_points", 0) <= int(config["SPARSE_COMPOSITE_HISTORY_MAX_POINTS"])
                and _safe_float(row.get("Composite_Score")) is not None
                and composite_universe_median is not None
                and (composite_universe_median - _safe_float(row.get("Composite_Score"))) >= float(config["MIN_COMPOSITE_MEDIAN_CONFIRMATION_GAP"])
            ):
                comp_trend_parts.append("Comp<Med")
        row_copy["Composite_Trend_Val"] = ", ".join(comp_trend_parts) if comp_trend_parts else "-"

        row_copy["_Sort_RS_Persistence"] = int(evidence.get("rs_persistence_days", 0) or 0)
        row_copy["_Sort_Composite_Persistence"] = int(evidence.get("composite_persistence_days", 0) or 0)
        row_copy["_Sort_RS_Drop"] = _safe_float(evidence.get("rs_drop_recent")) or 0.0
        row_copy["_Sort_Composite_Drop"] = _safe_float(evidence.get("composite_drop_recent")) or 0.0
        row_copy["_Sort_Leadership_Loss_Days"] = int(
            evidence.get(
                "leadership_loss_days",
                int(config["SORT_LEADERSHIP_MISSING_SENTINEL"]),
            )
            or int(config["SORT_LEADERSHIP_MISSING_SENTINEL"])
        )
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
    return distribution_watchlist.head(effective_top_n)
