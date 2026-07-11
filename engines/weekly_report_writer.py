from pathlib import Path

from engines.weekly_intelligence_engine import (
    WeeklyIntelligenceEngine,
    WeeklyReport,
)


class WeeklyReportWriter:

    OUTPUT_DIR = Path("reports")

    def write(self, report: WeeklyReport) -> Path:

        self.OUTPUT_DIR.mkdir(exist_ok=True)

        filename = (
            f"{report.window.start_date}"
            f"_to_"
            f"{report.window.end_date}"
            f"_WEEKLY_INTELLIGENCE.md"
        )

        output_file = self.OUTPUT_DIR / filename

        historical = report.historical

        emerging_count = len(historical.get("emerging_candidates", []))
        weakening_count = len(historical.get("weakening_candidates", []))
        theme_series_count = len(historical.get("theme_daily_series", {}))
        theme_delta_count = len(historical.get("theme_daily_deltas", {}))

        lines = []

        lines.append("# TABELA WEEKLY INTELLIGENCE")
        lines.append("")
        lines.append("## PERIOD")
        lines.append("")
        lines.append(f"Start Date      : {report.window.start_date}")
        lines.append(f"End Date        : {report.window.end_date}")
        lines.append(f"Trading Days    : {len(report.window.runs)}")
        lines.append("")
        lines.append("## WEEKLY SUMMARY")
        lines.append("")
        lines.append(f"Historical Window   : {historical['window_days']} days")
        lines.append(f"Rotation Date       : {historical['daily_rotation_date']}")
        lines.append(f"Emerging Themes     : {emerging_count}")
        lines.append(f"Weakening Themes    : {weakening_count}")
        lines.append("")
        lines.append("## DATA AVAILABLE")
        lines.append("")
        lines.append("✓ Historical Query Engine")
        lines.append("✓ Historical Intelligence")
        lines.append("✓ Weekly Intelligence")
        lines.append("")
        lines.append("## DATASET STATISTICS")
        lines.append("")
        lines.append(f"Theme Daily Series  : {theme_series_count}")
        lines.append(f"Theme Daily Deltas  : {theme_delta_count}")

        output_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return output_file


if __name__ == "__main__":

    engine = WeeklyIntelligenceEngine()

    report = engine.build()

    writer = WeeklyReportWriter()

    path = writer.write(report)

    print(path)