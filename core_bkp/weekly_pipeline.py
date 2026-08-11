from dataclasses import dataclass
from datetime import datetime

from engines.historical_intelligence_engine import (
    compute_historical_intelligence,
)

from engines.weekly_dataset_builder import (
    WeeklyDataset,
    WeeklyDatasetBuilder,
)


# =============================================================================
# WEEKLY REPORT
# =============================================================================

@dataclass(slots=True)
class WeeklyReport:

    dataset: WeeklyDataset

    historical: dict

    generated_at: datetime


# =============================================================================
# WEEKLY INTELLIGENCE ENGINE
# =============================================================================

class WeeklyIntelligenceEngine:

    def __init__(self):

        self.builder = WeeklyDatasetBuilder()

    # -------------------------------------------------------------------------
    # Build Weekly Report
    # -------------------------------------------------------------------------

    def build(
        self,
        trading_days: int = 5,
    ) -> WeeklyReport:

        dataset = self.builder.build(
            trading_days=trading_days,
        )

        historical = compute_historical_intelligence(
            max_days=trading_days,
        )

        return WeeklyReport(
            dataset=dataset,
            historical=historical,
            generated_at=datetime.now(),
        )


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":

    engine = WeeklyIntelligenceEngine()

    report = engine.build()

    print("=" * 70)
    print("TABELA WEEKLY INTELLIGENCE")
    print("=" * 70)

    print(f"Start Date   : {report.dataset.metadata.start_date}")
    print(f"End Date     : {report.dataset.metadata.end_date}")
    print(f"Trading Days : {report.dataset.metadata.trading_days}")
    print(f"Themes       : {len(report.dataset.themes)}")

    print()

    largest = report.dataset.rotation.get(
        "largest_rank_improvement"
    )

    print("Largest Weekly Rank Improvement")

    if largest:

        print(
            f"{largest['theme']} : "
            f"{largest['start_rank']} -> "
            f"{largest['end_rank']}"
        )
    else:
        print("None")

    print()

    print("Historical Sections")

    for key in report.historical.keys():

        print(f" - {key}")