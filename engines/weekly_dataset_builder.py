"""
===============================================================================
TABELA Weekly Dataset Builder
===============================================================================

Builds the reusable WeeklyDataset intelligence object.

This module performs NO presentation.

Consumers:
- Weekly Intelligence Engine
- Weekly Report Writer
- Dashboard (future)
- Monthly Intelligence (future)
- Quarterly Intelligence (future)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from engines.historical_query_engine import (
    Run,
    load_history,
)

from engines.historical_queries import HistoricalQueries
from datetime import date, datetime


# =============================================================================
# WEEKLY METADATA
# =============================================================================

@dataclass(slots=True)
class WeeklyMetadata:

    start_date: date
    end_date: date
    trading_days: int

# =============================================================================
# WEEKLY DATASET
# =============================================================================



@dataclass(slots=True)
class WeeklyDataset:

    metadata: WeeklyMetadata

    generated_at: datetime

    runs: list[Run] = field(default_factory=list)

    themes: dict[str, Any] = field(default_factory=dict)

    rotation: dict[str, Any] = field(default_factory=dict)

    leadership: dict[str, Any] = field(default_factory=dict)

    breadth: dict[str, Any] = field(default_factory=dict)

    stocks: dict[str, Any] = field(default_factory=dict)

    taxonomy: dict[str, Any] = field(default_factory=dict)

# =============================================================================
# WEEKLY DATASET BUILDER
# =============================================================================

class WeeklyDatasetBuilder:

    def __init__(self):

        self.history = load_history()

        self.queries = HistoricalQueries(self.history)

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    def build_metadata(
        self,
        runs: list[Run],
    ) -> WeeklyMetadata:

        if not runs:
            raise ValueError("No historical runs available.")

        return WeeklyMetadata(
            start_date=runs[0].date,
            end_date=runs[-1].date,
            trading_days=len(runs),
        )

    # -------------------------------------------------------------------------
    # Runs
    # -------------------------------------------------------------------------

    def build_runs(
        self,
        trading_days: int = 5,
    ) -> list[Run]:

        runs = self.queries.latest_n_runs(trading_days)

        if not runs:
            raise ValueError("No historical runs found.")

        return runs

    # -------------------------------------------------------------------------
    # Build
    # -------------------------------------------------------------------------

    def build(
        self,
        trading_days: int = 5,
    ) -> WeeklyDataset:

        import csv
        from pathlib import Path

        runs = self.build_runs(trading_days)

        metadata = self.build_metadata(runs)

        themes = self.build_theme_dataset(runs)

        rotation = self.compute_rotation(themes)

        leadership = self.compute_leadership(themes)

        breadth = self.compute_breadth(themes)

        stocks = self.compute_stock_intelligence(runs)

        #
        # ------------------------------------------------------------------
        # Taxonomy
        # ------------------------------------------------------------------
        #

        taxonomy = {
            "theme_to_industries": {},
            "theme_to_companies": {},
        }

        industry_file = Path("data//industry_theme_mapping.csv")

        if industry_file.exists():

            with open(industry_file, newline="", encoding="utf-8") as f:

                reader = csv.DictReader(f)

                for row in reader:

                    theme = row["Theme"].strip()
                    industry = row["Industry"].strip()

                    taxonomy["theme_to_industries"].setdefault(
                        theme,
                        []
                    ).append(industry)

        company_file = Path("data/stock_theme_mapping.csv")

        if company_file.exists():

            with open(company_file, newline="", encoding="utf-8") as f:

                reader = csv.DictReader(f)

                for row in reader:

                    theme = row["Theme"].strip()
                    ticker = row["Ticker"].strip()

                    taxonomy["theme_to_companies"].setdefault(
                        theme,
                        []
                    ).append(ticker)

        #
        # Taxonomy Summary
        #

        taxonomy["summary"] = {
            "theme_count": len(
                taxonomy["theme_to_industries"]
            ),
            "industry_count": sum(
                len(v)
                for v in taxonomy["theme_to_industries"].values()
            ),
            "company_count": sum(
                len(v)
                for v in taxonomy["theme_to_companies"].values()
            ),
        }


        dataset = WeeklyDataset(
            metadata=metadata,
            generated_at=datetime.now(),
            runs=runs,
            themes=themes,
            rotation=rotation,
            leadership=leadership,
            breadth=breadth,
            stocks=stocks,
            taxonomy=taxonomy,
        )

     

        return dataset

    # Weekly Stock Intelligence
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
# Weekly Stock Intelligence
# -------------------------------------------------------------------------
    def compute_stock_intelligence(
        self,
        runs: list[Run],
    ) -> dict[str, list[dict]]:

        import json
        from pathlib import Path

        long_counts = {}
        short_counts = {}

        watchlist_dir = Path("market_data/watchlist_history")

        for run in runs:

            watchlist_file = (
                watchlist_dir /
                f"watchlist_{run.date}.json"
            )

            if not watchlist_file.exists():
                continue

            with open(watchlist_file, "r", encoding="utf-8") as f:
                watchlist = json.load(f)

            #
            # Long
            #
            for item in watchlist.get("long", []):

                if isinstance(item, str):
                    ticker = item
                    theme = "Unknown"
                else:
                    ticker = item.get("ticker")
                    theme = item.get("theme", "Unknown")

                if ticker not in long_counts:

                    long_counts[ticker] = {
                        "ticker": ticker,
                        "theme": theme,
                        "days": 0,
                    }

                long_counts[ticker]["days"] += 1

                if (
                    long_counts[ticker]["theme"] == "Unknown"
                    and theme != "Unknown"
                ):
                    long_counts[ticker]["theme"] = theme

            #
            # Short
            #
            for item in watchlist.get("short", []):

                if isinstance(item, str):
                    ticker = item
                    theme = "Unknown"
                else:
                    ticker = item.get("ticker")
                    theme = item.get("theme", "Unknown")

                if ticker not in short_counts:

                    short_counts[ticker] = {
                        "ticker": ticker,
                        "theme": theme,
                        "days": 0,
                    }

                short_counts[ticker]["days"] += 1

                if (
                    short_counts[ticker]["theme"] == "Unknown"
                    and theme != "Unknown"
                ):
                    short_counts[ticker]["theme"] = theme

        long_list = [
            stock
            for stock in long_counts.values()
            if stock["days"] >= 4
        ]

        short_list = [
            stock
            for stock in short_counts.values()
            if stock["days"] >= 4
        ]

        long_list.sort(
            key=lambda x: (-x["days"], x["ticker"])
        )

        short_list.sort(
            key=lambda x: (-x["days"], x["ticker"])
        )

        return {
            "long": long_list,
            "short": short_list,
        }

    # -------------------------------------------------------------------------
    # Theme Dataset
    # -------------------------------------------------------------------------

    def build_theme_dataset(
        self,
        runs: list[Run],
    ) -> dict[str, Any]:

        themes: dict[str, dict] = {}

        groups = (
            "leading_themes",
            "neutral_themes",
            "lagging_themes",
        )

        for run in runs:

            dataset = self.queries.dataset(run, "snapshot")

            if dataset is None or dataset.data is None:
                continue

            snapshot = dataset.data

            for group in groups:

                for item in snapshot.get(group, []):

                    theme = item["theme"]

                    if theme not in themes:

                        themes[theme] = {
                            "daily": [],
                        }

                    themes[theme]["daily"].append(
                        {
                            "date": run.date,
                            "classification": group.replace("_themes", ""),
                            "rank": item["rank"],
                            "score": item["score"],
                        }
                    )

        #
        # Build weekly statistics
        #

        for theme_data in themes.values():

            daily = sorted(
                theme_data["daily"],
                key=lambda x: x["date"],
            )

            ranks = [d["rank"] for d in daily]
            scores = [d["score"] for d in daily]

            theme_data["start_rank"] = ranks[0]
            theme_data["end_rank"] = ranks[-1]
            theme_data["best_rank"] = min(ranks)
            theme_data["worst_rank"] = max(ranks)
            theme_data["average_rank"] = sum(ranks) / len(ranks)

            theme_data["start_score"] = scores[0]
            theme_data["end_score"] = scores[-1]
            theme_data["best_score"] = max(scores)
            theme_data["worst_score"] = min(scores)
            theme_data["average_score"] = sum(scores) / len(scores)

            theme_data["days_seen"] = len(daily)

            theme_data["days_leading"] = sum(
                1 for d in daily
                if d["classification"] == "leading"
            )

            theme_data["days_neutral"] = sum(
                1 for d in daily
                if d["classification"] == "neutral"
            )

            theme_data["days_lagging"] = sum(
                1 for d in daily
                if d["classification"] == "lagging"
            )

        return themes

    # -------------------------------------------------------------------------
    # Weekly Rotation
    # -------------------------------------------------------------------------

    def compute_rotation(
        self,
        themes: dict[str, Any],
    ) -> dict[str, list[dict]]:

        rank_improvements = []
        rank_declines = []

        score_gains = []
        score_losses = []

        for theme, data in themes.items():

            rank_change = data["start_rank"] - data["end_rank"]
            score_change = data["end_score"] - data["start_score"]

            record = {
                "theme": theme,
                "rank_change": rank_change,
                "score_change": score_change,
                "start_rank": data["start_rank"],
                "end_rank": data["end_rank"],
                "start_score": data["start_score"],
                "end_score": data["end_score"],
            }

            if rank_change > 0:
                rank_improvements.append(record)
            elif rank_change < 0:
                rank_declines.append(record)

            if score_change > 0:
                score_gains.append(record)
            elif score_change < 0:
                score_losses.append(record)

        rank_improvements.sort(
            key=lambda x: x["rank_change"],
            reverse=True,
        )

        rank_declines.sort(
            key=lambda x: x["rank_change"],
        )

        score_gains.sort(
            key=lambda x: x["score_change"],
            reverse=True,
        )

        score_losses.sort(
            key=lambda x: x["score_change"],
        )

        return {
            "rank_improvements": rank_improvements[:10],
            "rank_declines": rank_declines[:10],
            "score_gains": score_gains[:10],
            "score_losses": score_losses[:10],

            "largest_rank_improvement": rank_improvements[0] if rank_improvements else None,
            "largest_rank_decline": rank_declines[0] if rank_declines else None,
            "largest_score_gain": score_gains[0] if score_gains else None,
            "largest_score_loss": score_losses[0] if score_losses else None,
        }

    # -------------------------------------------------------------------------
    # Leadership
    # -------------------------------------------------------------------------

    def compute_leadership(
        self,
        themes: dict[str, Any],
    ) -> dict[str, list]:

        persistent = []
        emerging = []
        weakening = []
        persistent_laggards = []

        for theme, data in themes.items():

            if data["days_leading"] == data["days_seen"]:
                persistent.append(theme)

            elif (
                data["days_leading"] > 0
                and data["end_rank"] <= 7
            ):
                emerging.append(theme)

            elif (
                data["start_rank"] <= 7
                and data["end_rank"] > 7
            ):
                weakening.append(theme)

            elif data["days_lagging"] == data["days_seen"]:
                persistent_laggards.append(theme)

        persistent.sort()
        emerging.sort()
        weakening.sort()
        persistent_laggards.sort()

        return {

            "persistent_leaders": persistent,

            "emerging_leaders": emerging,

            "weakening_leaders": weakening,

            "persistent_laggards": persistent_laggards,

        }

        # -------------------------------------------------------------------------
    
    # -------------------------------------------------------------------------
    # Breadth
    # -------------------------------------------------------------------------

    def compute_breadth(
        self,
        themes: dict[str, Any],
    ) -> dict[str, Any]:

        improving = sorted(
            themes.items(),
            key=lambda x: x[1]["average_score"],
            reverse=True,
        )

        weakening = sorted(
            themes.items(),
            key=lambda x: x[1]["average_score"],
        )

        return {

            "strongest_average": improving[:10],

            "weakest_average": weakening[:10],

        }

if __name__ == "__main__":

    builder = WeeklyDatasetBuilder()

    weekly = builder.build()

    print()
    print("Weekly Long Stocks")
    print(weekly.stocks["long"])

    print()
    print("Weekly Short Stocks")
    print(weekly.stocks["short"])

    print("=" * 70)
    print("TABELA WEEKLY DATASET BUILDER")
    print("=" * 70)

    print(f"Start Date   : {weekly.metadata.start_date}")
    print(f"End Date     : {weekly.metadata.end_date}")
    print(f"Trading Days : {weekly.metadata.trading_days}")
    print(f"Runs Loaded  : {len(weekly.runs)}")
    print(f"Themes Loaded : {len(weekly.themes)}")
    software = weekly.themes.get("Software")

    if software:

        print()
        print("Software")
        print(f"Start Rank : {software['start_rank']}")
        print(f"End Rank   : {software['end_rank']}")
        print(f"Days Seen  : {software['days_seen']}")
        print()
        print("Top Rank Improvement")

        top = weekly.rotation["rank_improvements"][0]

        print(
            f"{top['theme']} : "
            f"{top['start_rank']} -> {top['end_rank']}"
        )
        print()
        print(
            "Persistent Leaders :",
            len(weekly.leadership["persistent_leaders"])
        )

        print()
        print(
            "Strongest Average :",
            weekly.breadth["strongest_average"][0][0]
        )
        print()
        print("Dataset")
        print(f"Theme Count : {len(weekly.themes)}")

        if weekly.rotation["largest_rank_improvement"]:
            print(
                "Largest Improvement :",
                weekly.rotation["largest_rank_improvement"]["theme"]
            )
