from dataclasses import dataclass, field
from datetime import date, datetime

from engines.historical_intelligence_engine import (
    build_historical_intelligence_report,
)
from engines.historical_query_engine import load_history
from engines.historical_queries import HistoricalQueries


# =============================================================================
# WEEKLY WINDOW
# =============================================================================

@dataclass(slots=True)
class WeeklyWindow:
    start_date: date
    end_date: date
    runs: list


# =============================================================================
# WEEKLY REPORT
# =============================================================================

@dataclass(slots=True)
class WeeklyReport:
    window: WeeklyWindow
    historical: dict
    generated_at: datetime
    summary: dict = field(default_factory=dict)


# =============================================================================
# WEEKLY INTELLIGENCE ENGINE
# =============================================================================

class WeeklyIntelligenceEngine:

    def __init__(self):
        self.history = load_history()
        self.queries = HistoricalQueries(self.history)

    def latest_week(self) -> WeeklyWindow:

        runs = self.queries.latest_n_runs(5)

        return WeeklyWindow(
            start_date=runs[0].date,
            end_date=runs[-1].date,
            runs=runs,
        )

    def build(self) -> WeeklyReport:

        window = self.latest_week()

        historical = build_historical_intelligence_report(
            max_days=len(window.runs)
        )

        return WeeklyReport(
            window=window,
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

    print(f"Start : {report.window.start_date}")
    print(f"End   : {report.window.end_date}")
    print(f"Runs  : {len(report.window.runs)}")

    print()

    print("Historical Keys")

    for key in report.historical.keys():
        print(f" - {key}")