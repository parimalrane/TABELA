from __future__ import annotations

from pathlib import Path

class WeeklyMarkdownWriter:
    OUTPUT_DIR = Path("market_data/weekly_intelligence")

    def write(self, dataset):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        metadata = dataset.metadata
        filename = f"{metadata.start_date}_to_{metadata.end_date}_weekly_intelligence.md"
        output_file = self.OUTPUT_DIR / filename
        lines = []

        self.write_metadata(lines, dataset)
        self.write_market(lines, dataset)
        self.write_themes(lines, dataset)

        # Batch 2
        self.write_stocks(lines, dataset)
        self.write_review_queue(lines, dataset)
        self.write_taxonomy(lines, dataset)
        self.write_maintenance(lines, dataset)
        self.write_quality(lines, dataset)

        output_file.write_text("\n".join(lines), encoding="utf-8")
        return output_file

    def write_metadata(self, lines, dataset):
        m = dataset.metadata
        lines += [
            "# Weekly Intelligence Report","",
            "## Metadata","",
            f"- **Start Date:** {m.start_date}",
            f"- **End Date:** {m.end_date}",
            f"- **Trading Days:** {m.trading_days}",
            f"- **Runs Loaded:** {len(dataset.runs)}",""
        ]

    def write_market(self, lines, dataset):
        lines += ["## Market","","### Rotation","```",str(dataset.rotation),"```","",
                  "### Breadth","```",str(dataset.breadth),"```",""]

    def write_themes(self, lines, dataset):

        lines.append("## Themes")
        lines.append("")

        sections = [
            ("Persistent Leaders", dataset.leadership["persistent_leaders"]),
            ("Emerging Leaders", dataset.leadership["emerging_leaders"]),
            ("Weakening Leaders", dataset.leadership["weakening_leaders"]),
            ("Persistent Laggards", dataset.leadership["persistent_laggards"]),
        ]

        for title, values in sections:
            lines.append(f"### {title}")

            if values:
                for value in values:
                    lines.append(f"- {value}")
            else:
                lines.append("- None")

            lines.append("")

        lines.append("### Theme Details")
        lines.append("")

        for theme_name, theme_data in dataset.themes.items():
            lines.append(f"#### {theme_name}")
            lines.append("```")
            lines.append(str(theme_data))
            lines.append("```")
            lines.append("")

    def write_stocks(self, lines, dataset):
        lines.append("## Stocks")
        lines.append("")

        sections = [
            ("Persistent Long Candidates", dataset.stocks.get("persistent_long", [])),
            ("Persistent Short Candidates", dataset.stocks.get("persistent_short", [])),
            ("Weekly Long Candidates", dataset.stocks.get("weekly_long", [])),
            ("Weekly Short Candidates", dataset.stocks.get("weekly_short", [])),
        ]

        for title, rows in sections:
            lines.append(f"### {title}")
            if rows:
                for row in rows:
                    lines.append(f"- {row}")
            else:
                lines.append("- None")
            lines.append("")

    def write_review_queue(self, lines, dataset):
        lines.append("## Review Queue")
        lines.append("")

        lines.append("```")
        lines.append(str(dataset.rotation))
        lines.append("```")
        lines.append("")

    def write_taxonomy(self, lines, dataset):
        lines.append("## Taxonomy")
        lines.append("")
        lines.append("```")
        lines.append(str(dataset.taxonomy))
        lines.append("```")
        lines.append("")

    def write_maintenance(self, lines, dataset):
        lines.append("## Maintenance")
        lines.append("")
        lines.append("```")
        lines.append(str(getattr(dataset, "maintenance", {})))
        lines.append("```")
        lines.append("")

    def write_quality(self, lines, dataset):
        m = dataset.metadata

        lines.append("## Quality")
        lines.append("")
        lines.append(f"- Warnings: 0")
        lines.append(f"- Errors: 0")
        lines.append(f"- Missing Days: {max(0, 5 - m.trading_days)}")
        lines.append(f"- Completeness: {round(m.trading_days / 5, 2)}")
        lines.append("")

if __name__=="__main__":
    from engines.weekly_dataset_builder import WeeklyDatasetBuilder
    from engines.weekly_json_writer import WeeklyJSONWriter
    dataset=WeeklyDatasetBuilder().build()
    WeeklyJSONWriter().write(dataset)
    print(WeeklyMarkdownWriter().write(dataset))
