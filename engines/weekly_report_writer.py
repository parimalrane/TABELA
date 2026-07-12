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


        self._render_stock_intelligence(
            lines,
            report.dataset.stocks,
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
        decline = summary["largest_rank_decline"]
        gain = summary["largest_score_gain"]
        loss = summary["largest_score_loss"]

        if improvement:

            lines.append(
                f"Largest Rank Improvement : "
                f"{improvement['theme']} "
                f"({improvement['start_rank']} → "
                f"{improvement['end_rank']})"
            )

        if decline:

            lines.append(
                f"Largest Rank Decline     : "
                f"{decline['theme']} "
                f"({decline['start_rank']} → "
                f"{decline['end_rank']})"
            )

        if gain:

            lines.append(
                f"Largest Score Gain       : "
                f"{gain['theme']} "
                f"({gain['score_change']:+.2f})"
            )

        if loss:

            lines.append(
                f"Largest Score Loss       : "
                f"{loss['theme']} "
                f"({loss['score_change']:+.2f})"
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

        self._write_rotation(
            lines,
            "Top Score Gains",
            rotation["score_gains"],
            score_mode=True,
        )

        self._write_rotation(
            lines,
            "Top Score Losses",
            rotation["score_losses"],
            score_mode=True,
        )

    def _render_theme_performance(
        self,
        lines,
        themes,
    ):

        lines.append("## THEME PERFORMANCE")
        lines.append("")

        lines.append(
            "| Theme | Start | End | ΔRank | Start Score | End Score | ΔScore | Leading | Seen |"
        )

        lines.append(
            "|------|------:|----:|------:|------------:|----------:|-------:|---------:|----:|"
        )

        ranked = sorted(
            themes.items(),
            key=lambda x: x[1]["end_rank"],
        )

        for theme, data in ranked:

            rank_delta = data["start_rank"] - data["end_rank"]

            score_delta = (
                data["end_score"]
                - data["start_score"]
            )

            lines.append(
                f"| {theme} | "
                f"{data['start_rank']} | "
                f"{data['end_rank']} | "
                f"{rank_delta:+d} | "
                f"{data['start_score']:.2f} | "
                f"{data['end_score']:.2f} | "
                f"{score_delta:+.2f} | "
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
        lines.append("*Initial implementation*")
        lines.append("")

        strongest = breadth["strongest_average"]

        if strongest:

            lines.append("| Theme | Weekly Average Score |")
            lines.append("|------|----------:|")

            for theme, data in strongest[:10]:

                lines.append(
                    f"| {theme} | {data['average_score']:.2f} |"
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
            f"History Window : {historical['window_days']} trading days"
        )

        lines.append(
            f"Latest Rotation : {historical['daily_rotation_date']}"
        )

        lines.append("")

        if historical.get("emerging_candidates"):

            lines.append("### Emerging Themes")

            for item in historical["emerging_candidates"][:5]:

                lines.append(f"• {item['theme']}")
                lines.append(
                    f"  Rank : {item['first_rank']} → "
                    f"{item['last_rank']} "
                    f"({item['rank_improvement']:+d})"
                )
                lines.append(
                    f"  Score: {item['first_score']:.2f} → "
                    f"{item['last_score']:.2f} "
                    f"({item['score_improvement']:+.2f})"
                )

                if item.get("class_transitions"):

                    lines.append(
                        f"  Transition: "
                        f"{', '.join(item['class_transitions'])}"
                    )

                lines.append("")

            lines.append("")

        if historical.get("weakening_candidates"):

            lines.append("### Weakening Themes")

            for item in historical["weakening_candidates"][:5]:

                lines.append(f"• {item['theme']}")
                lines.append(
                    f"  Rank : {item['first_rank']} → "
                    f"{item['last_rank']} "
                    f"(-{item['rank_deterioration']})"
                )
                lines.append(
                    f"  Score: {item['first_score']:.2f} → "
                    f"{item['last_score']:.2f} "
                    f"(-{item['score_decline']:.2f})"
                )

                if item.get("class_transitions"):

                    lines.append(
                        f"  Transition: "
                        f"{', '.join(item['class_transitions'])}"
                    )

                lines.append("")

            lines.append("")

    def _render_statistics(
        self,
        lines,
        report,
    ):

        metadata = report.dataset.metadata

        lines.append("## DATASET STATISTICS")
        lines.append("")

        lines.append(f"Trading Days : {metadata.trading_days}")
        lines.append(f"Runs Loaded  : {len(report.dataset.runs)}")
        lines.append(f"Themes       : {len(report.dataset.themes)}")
        lines.append(f"Generated    : {report.generated_at:%Y-%m-%d %H:%M:%S}")
        lines.append("")

    def _render_stock_intelligence(
        self,
        lines,
        stocks,
    ):

        lines.append("## WEEKLY STOCK INTELLIGENCE")
        lines.append("")

        #
        # Long
        #
        lines.append("### Institutional Long Leaders")
        lines.append("")

        if stocks["long"]:

            lines.append("| Ticker | Days |")
            lines.append("|--------|-----:|")

            for stock in stocks["long"]:

                lines.append(
                    f"| {stock['ticker']} | "
                    f"{stock['days']}/5 |"
                )

        else:

            lines.append("No institutional long leaders (4+/5 days).")

        lines.append("")
        #
        # Short
        #
        lines.append("### Institutional Short Leaders")
        lines.append("")

        if stocks["short"]:

            lines.append("| Ticker | Days |")
            lines.append("|--------|-----:|")

            for stock in stocks["short"]:

                lines.append(
                    f"| {stock['ticker']} | "
                    f"{stock['days']}/5 |"
                )

        else:

            lines.append("No institutional short leaders (4+/5 days).")

        lines.append("")

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
        score_mode=False,
    ):

        lines.append(f"### {title}")

        if not items:

            lines.append("- None")
            lines.append("")
            return

        for item in items:

            if score_mode:

                lines.append(
                    f"- {item['theme']}: "
                    f"{item['score_change']:+.2f}"
                )

            else:

                rank_delta = (
                    item["start_rank"]
                    - item["end_rank"]
                )

                lines.append(
                    f"- {item['theme']}: "
                    f"{item['start_rank']} → "
                    f"{item['end_rank']} "
                    f"({rank_delta:+d})"
                )

        lines.append("")

if __name__ == "__main__":

    engine = WeeklyIntelligenceEngine()

    report = engine.build()

    writer = WeeklyReportWriter()

    path = writer.write(report)

    print(path)
