from pathlib import Path

from engines.weekly_intelligence_engine import (
    WeeklyIntelligenceEngine,
WeeklyReport,
)

class WeeklyReportWriter:
    OUTPUT_DIR = Path("reports")

    def write(self, report: WeeklyReport) -> Path:

        self.OUTPUT_DIR.mkdir(exist_ok=True)

        metadata = report.dataset.metadata
        summary = report.dataset.summary
        leadership = report.dataset.leadership
        rotation = report.dataset.rotation
        themes = report.dataset.themes
        breadth = report.dataset.breadth

        filename = (
            f"{metadata.start_date}"
            f"_to_"
            f"{metadata.end_date}"
            f"_WEEKLY_INTELLIGENCE.md"
        )

        output_file = self.OUTPUT_DIR / filename

        lines = []

        self._render_header(lines)

        self._render_executive_summary(
            lines,
            metadata,
            summary,
        )

        self._render_leadership(
            lines,
            leadership,
        )

        self._render_rotation(
            lines,
            rotation,
        )

        self._render_theme_performance(
            lines,
            themes,
        )

        self._render_breadth(
            lines,
            breadth,
        )

        self._render_historical(
            lines,
            report.historical,
        )

        self._render_statistics(
            lines,
            report,
        )

        output_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return output_file

    def _render_header(
        self,
        lines,
    ):

        lines.append("# TABELA WEEKLY INTELLIGENCE")
        lines.append("")
        
    def _render_executive_summary(
        self,
        lines,
        metadata,
        summary,
    ):

        lines.append("## EXECUTIVE SUMMARY")
        lines.append("")

        lines.append(f"Start Date      : {metadata.start_date}")
        lines.append(f"End Date        : {metadata.end_date}")
        lines.append(f"Trading Days    : {metadata.trading_days}")
        lines.append(f"Themes          : {summary['theme_count']}")

        lines.append("")

        improvement = summary["largest_rank_improvement"]

        if improvement:

            lines.append(
                f"Largest Rank Improvement : "
                f"{improvement['theme']} "
                f"({improvement['start_rank']} → "
                f"{improvement['end_rank']})"
            )

        decline = summary["largest_rank_decline"]

        if decline:

            lines.append(
                f"Largest Rank Decline     : "
                f"{decline['theme']} "
                f"({decline['start_rank']} → "
                f"{decline['end_rank']})"
            )

        lines.append("")

    def _render_leadership(
        self,
        lines,
        leadership,
    ):

        lines.append("## LEADERSHIP")
        lines.append("")

        self._write_list(
            lines,
            f"Persistent Leaders ({len(leadership['persistent_leaders'])})",
            leadership["persistent_leaders"],
        )

        self._write_list(
            lines,
            f"Emerging Leaders ({len(leadership['emerging_leaders'])})",
            leadership["emerging_leaders"],
        )

        self._write_list(
            lines,
            f"Weakening Leaders ({len(leadership['weakening_leaders'])})",
            leadership["weakening_leaders"],
        )

        self._write_list(
            lines,
            f"Persistent Laggards ({len(leadership['persistent_laggards'])})",
            leadership["persistent_laggards"],
        )

    def _render_rotation(
        self,
        lines,
        rotation,
    ):

        lines.append("## WEEKLY ROTATION")
        lines.append("")

        self._write_rotation(
            lines,
            "Top Rank Improvements",
            rotation["rank_improvements"],
        )

        self._write_rotation(
            lines,
            "Top Rank Declines",
            rotation["rank_declines"],
        )

    def _render_theme_performance(
        self,
        lines,
        themes,
    ):

        lines.append("## THEME PERFORMANCE")
        lines.append("")

        lines.append(
            "| Theme | Start | End | Avg | Leading | Seen |"
        )

        lines.append(
            "|------|------:|----:|----:|--------:|----:|"
        )

        for theme in sorted(themes):

            data = themes[theme]

            lines.append(
                f"| {theme} | "
                f"{data['start_rank']} | "
                f"{data['end_rank']} | "
                f"{data['average_rank']:.1f} | "
                f"{data['days_leading']} | "
                f"{data['days_seen']} |"
            )

        lines.append("")

    def _render_breadth(
        self,
        lines,
        breadth,
    ):

        lines.append("## BREADTH")
        lines.append("")

        strongest = breadth["strongest_average"][0]

        lines.append(
            f"Strongest Average Theme : {strongest[0]}"
        )

        lines.append("")

    def _render_historical(
        self,
        lines,
        historical,
    ):

        lines.append("## HISTORICAL INTELLIGENCE")
        lines.append("")

        lines.append(
            f"Window Days : {historical['window_days']}"
        )

        lines.append(
            f"Rotation Date : {historical['daily_rotation_date']}"
        )

        lines.append("")

    def _render_statistics(
        self,
        lines,
        report,
    ):

        lines.append("## DATASET STATISTICS")
        lines.append("")

        lines.append(
            f"Runs Loaded : {len(report.dataset.runs)}"
        )

        lines.append(
            f"Themes : {len(report.dataset.themes)}"
        )

    # ==============================================================
    # Helpers
    # ==============================================================

    def _write_list(
        self,
        lines,
        title,
        items,
    ):

        lines.append(f"### {title}")

        if not items:

            lines.append("- None")
            lines.append("")
            return

        for item in items:

            lines.append(f"- {item}")

        lines.append("")

    def _write_rotation(
        self,
        lines,
        title,
        items,
    ):

        lines.append(f"### {title}")

        if not items:

            lines.append("- None")
            lines.append("")
            return

        for item in items:

            lines.append(
                f"- {item['theme']} : "
                f"{item['start_rank']} → "
                f"{item['end_rank']}"
            )

        lines.append("")

if __name__ == "__main__":

    engine = WeeklyIntelligenceEngine()

    report = engine.build()

    writer = WeeklyReportWriter()

    path = writer.write(report)

    print(path)