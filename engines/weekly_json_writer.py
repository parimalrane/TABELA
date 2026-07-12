from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path


class WeeklyJSONWriter:

    OUTPUT_DIR = Path("market_data/weekly_intelligence")

    def write(self, dataset):

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        metadata = dataset.metadata

        filename = (
            f"{metadata.start_date}"
            "_to_"
            f"{metadata.end_date}"
            "_weekly_intelligence.json"
        )

        output_file = self.OUTPUT_DIR / filename

        data = {

            "metadata": {

                "schema_version": "1.0",

                "generated_at": dataset.generated_at.isoformat(),

                "start_date": str(metadata.start_date),

                "end_date": str(metadata.end_date),

                "trading_days": metadata.trading_days,

                "runs_loaded": len(dataset.runs),

            },

            "market": {

                "rotation": dataset.rotation,

                "breadth": dataset.breadth,

            },

            "themes": {

                "persistent_leaders":
                    dataset.leadership["persistent_leaders"],

                "emerging_leaders":
                    dataset.leadership["emerging_leaders"],

                "weakening_leaders":
                    dataset.leadership["weakening_leaders"],

                "persistent_laggards":
                    dataset.leadership["persistent_laggards"],

                "details":
                    dataset.themes,

            },

            "stocks": dataset.stocks,

            "review_queue": {

                "persistent_long_candidates":
                    dataset.stocks["long"],

                "persistent_short_candidates":
                    dataset.stocks["short"],

                "largest_rank_improvements":
                    dataset.rotation["rank_improvements"][:5],

                "largest_rank_declines":
                    dataset.rotation["rank_declines"][:5],

                "largest_score_gains":
                    dataset.rotation["score_gains"][:5],

                "largest_score_losses":
                    dataset.rotation["score_losses"][:5],

                "emerging_themes":
                    dataset.leadership["emerging_leaders"],

                "weakening_themes":
                    dataset.leadership["weakening_leaders"],

            },

            "taxonomy": dataset.taxonomy,

            #
            # Builder owns maintenance.
            #

            "maintenance":
                getattr(dataset, "maintenance", {}),

            "quality": {

                "warnings": [],

                "errors": [],

                "missing_days":
                    max(0, 5 - metadata.trading_days),

                "completeness":
                    round(metadata.trading_days / 5, 2),

            }

        }

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                default=self._json_default,
            )

        return output_file

    @staticmethod
    def _json_default(obj):

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return str(obj)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    from engines.weekly_dataset_builder import WeeklyDatasetBuilder

    print("=" * 70)
    print("TABELA WEEKLY JSON WRITER")
    print("=" * 70)

    builder = WeeklyDatasetBuilder()

    dataset = builder.build()

    output = WeeklyJSONWriter().write(dataset)

    print()
    print("Weekly Intelligence JSON Generated")
    print(output)
    print()