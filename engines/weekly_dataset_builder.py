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

    maintenance: dict[str, Any] = field(default_factory=dict)

class WeeklyDatasetBuilder:

    def __init__(self):

        self.history = load_history()

        self.queries = HistoricalQueries(self.history)

    def build_runs(
        self,
        trading_days: int = 5,
    ) -> list[Run]:

        runs = self.queries.latest_n_runs(trading_days)

        if not runs:
            raise ValueError("No historical runs found.")

        return runs

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

        persistent = self.compute_stock_intelligence(runs)

        weekly = self.compute_weekly_stock_history(runs)

        stocks = {

            "persistent_long": persistent["long"],

            "persistent_short": persistent["short"],

            "weekly_long": weekly["long"],

            "weekly_short": weekly["short"],

            "transition_registry": self.load_stock_transition_registry(),

        }

        unknown = self.compute_unknown_intelligence(runs)

        #
        # ------------------------------------------------------------------
        # Taxonomy
        # ------------------------------------------------------------------
        #

        taxonomy = {
            "theme_to_industries": {},
            "theme_to_companies": {},
        }

        industry_file = Path("data/industry_theme_mapping.csv")

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

        taxonomy["summary"] = {

            "theme_count":
                len(taxonomy["theme_to_industries"]),

            "industry_count":
                sum(
                    len(v)
                    for v in taxonomy["theme_to_industries"].values()
                ),

            "company_count":
                sum(
                    len(v)
                    for v in taxonomy["theme_to_companies"].values()
                ),
        }

        #
        maintenance = {

        "taxonomy_review": {

            "status": "pending_ai_review",

            "last_reviewed": str(metadata.end_date),

            # Existing unknown evidence
            "unknown": unknown,

            # Existing stock persistence evidence
            "stock_transition_registry":
                stocks["transition_registry"],

            # Existing theme evidence
            "theme_transitions": {

                theme: data["transitions"]

                for theme, data in themes.items()

            },

            # Existing weekly theme history
            "theme_history": {

                theme: data["daily"]

                for theme, data in themes.items()

            },

        }

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

            maintenance=maintenance,

        )


        return dataset

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

    def compute_weekly_stock_history(
        self,
        runs: list[Run],
    ) -> dict[str, list[dict]]:

        import json
        from pathlib import Path

        watchlist_dir = Path("market_data/watchlist_history")
        stock_history_dir = Path("market_data/stock_universe")

        weekly_long = {}
        weekly_short = {}

        for run in runs:

            watchlist_file = (
                watchlist_dir /
                f"watchlist_{run.date}.json"
            )

            history_file = (
                stock_history_dir /
                f"{run.date}_stock_history.json"
            )

            if (
                not watchlist_file.exists()
                or
                not history_file.exists()
            ):
                continue

            with open(
                watchlist_file,
                "r",
                encoding="utf-8",
            ) as f:

                watchlist = json.load(f)

            with open(
                history_file,
                "r",
                encoding="utf-8",
            ) as f:

                stock_history = json.load(f)

            history_lookup = {

                stock["ticker"]: stock

                for stock in stock_history

            }

            #
            # LONG
            #

            for item in watchlist.get("long", []):

                ticker = (
                    item
                    if isinstance(item, str)
                    else item["ticker"]
                )

                if ticker not in history_lookup:
                    continue

                stock = history_lookup[ticker]

                weekly_long.setdefault(

                    ticker,

                    {

                        "ticker": ticker,

                        "theme": stock.get("theme"),

                        "days": 0,

                        "history": [],

                    }

                )

                weekly_long[ticker]["days"] += 1

                weekly_long[ticker]["history"].append(

                    {

                        "date": run.date,

                        "theme": stock.get("theme"),

                        "theme_rank": stock.get("theme_rank"),

                        "theme_class": stock.get("theme_class"),

                        "theme_strength_score":
                            stock.get("theme_strength_score"),

                        "long_rank":
                            stock.get("long_rank"),

                        "rs_rating":
                            stock.get("rs_rating"),

                        "long_score":
                            stock.get("long_score"),

                        "composite_score":
                            stock.get("composite_score"),

                    }

                )

            #
            # SHORT
            #

            for item in watchlist.get("short", []):

                ticker = (
                    item
                    if isinstance(item, str)
                    else item["ticker"]
                )

                if ticker not in history_lookup:
                    continue

                stock = history_lookup[ticker]

                weekly_short.setdefault(

                    ticker,

                    {

                        "ticker": ticker,

                        "theme": stock.get("theme"),

                        "days": 0,

                        "history": [],

                    }

                )

                weekly_short[ticker]["days"] += 1

                weekly_short[ticker]["history"].append(

                    {

                        "date": run.date,

                        "theme": stock.get("theme"),

                        "theme_rank": stock.get("theme_rank"),

                        "theme_class": stock.get("theme_class"),

                        "theme_strength_score":
                            stock.get("theme_strength_score"),

                        "short_rank":
                            stock.get("short_rank"),

                        "rs_rating":
                            stock.get("rs_rating"),

                        "short_score":
                            stock.get("short_score"),

                        "composite_score":
                            stock.get("composite_score"),

                    }

                )

        return {

            "long": sorted(

                weekly_long.values(),

                key=lambda x: (

                    -x["days"],

                    x["ticker"],

                ),

            ),

            "short": sorted(

                weekly_short.values(),

                key=lambda x: (

                    -x["days"],

                    x["ticker"],

                ),

            ),

        }


    def load_stock_transition_registry(
        self,
    ) -> dict:

        import json
        from pathlib import Path

        filename = Path(
            "market_data/stock_transition_registry.json"
        )

        if not filename.exists():
            return {}

        with open(
            filename,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)


    def compute_unknown_intelligence(
        self,
        runs: list[Run],
    ) -> dict[str, Any]:

        import json
        from pathlib import Path

        unknown_dir = Path("market_data/unknown_classification")

        company_counts = {}

        industry_counts = {}

        sector_counts = {}

        for run in runs:

            filename = (
                unknown_dir /
                f"{run.date}_unknown_classification.json"
            )

            if not filename.exists():
                continue

            with open(filename, "r", encoding="utf-8") as f:

                payload = json.load(f)

            for stock in payload.get("unknown_leaders", []):

                ticker = stock["ticker"]

                if ticker not in company_counts:

                    company_counts[ticker] = {

                        "ticker": ticker,

                        "company_name": stock.get("company_name", ""),
                        
                        "industry": stock.get("industry", "Unknown"),
                        
                        "sector": stock.get("sector", "Unknown"),

                        "days": 0,

                        "total_rs": 0,

                        "total_long_score": 0,

                    }

                company_counts[ticker]["days"] += 1

                company_counts[ticker]["total_rs"] += stock.get("rs_rating", 0)

                company_counts[ticker]["total_long_score"] += stock.get("long_score", 0)

                industry = stock["industry"]

                industry_counts[industry] = (
                    industry_counts.get(industry, 0) + 1
                )

                sector = stock["sector"]

                sector_counts[sector] = (
                    sector_counts.get(sector, 0) + 1
                )

        persistent = []

        emerging = []

        for item in company_counts.values():

            item["average_rs"] = round(
                item["total_rs"] / item["days"],
                1,
            )

            item["average_long_score"] = round(
                item["total_long_score"] / item["days"],
                2,
            )

            del item["total_rs"]

            del item["total_long_score"]

            if item["days"] >= 4:

                persistent.append(item)

            else:

                emerging.append(item)

        persistent.sort(
            key=lambda x: (
                -x["days"],
                -x["average_rs"],
                x["ticker"],
            )
        )

        emerging.sort(
            key=lambda x: (
                -x["days"],
                -x["average_rs"],
                x["ticker"],
            )
        )

        unknown_industries = [

            {

                "industry": industry,

                "occurrences": count,

            }

            for industry, count in sorted(

                industry_counts.items(),

                key=lambda x: (-x[1], x[0])

            )

        ]

        unknown_sectors = [

            {

                "sector": sector,

                "occurrences": count,

            }

            for sector, count in sorted(

                sector_counts.items(),

                key=lambda x: (-x[1], x[0])

            )

        ]

        return {

            "persistent_unknowns": persistent,

            "emerging_unknowns": emerging,

            "unknown_industries": unknown_industries,

            "unknown_sectors": unknown_sectors,

        }

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

            # ---------------------------------
            # Theme transition timeline
            # ---------------------------------

            transitions = []

            for previous, current in zip(
                daily,
                daily[1:],
            ):

                if previous["classification"] != current["classification"]:

                    transitions.append(
                        {
                            "date": current["date"],
                            "from": previous["classification"],
                            "to": current["classification"],
                        }
                    )

            theme_data["transitions"] = transitions

            # ---------------------------------
            # Weekly statistics
            # ---------------------------------

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
