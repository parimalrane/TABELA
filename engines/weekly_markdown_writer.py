
from __future__ import annotations

from pathlib import Path


class WeeklyMarkdownWriter:
    """
    Presentation-only writer.

    Uses the same dataset consumed by WeeklyJSONWriter.
    Performs no calculations.
    """

    OUTPUT_DIR = Path("market_data/weekly_intelligence")

    def write(self, json_file: Path):

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        import json

        json_file = Path(json_file)

        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        output_file = (
            self.OUTPUT_DIR /
            json_file.with_suffix(".md").name
        )

        

        lines = []

        for key, value in data.items():
            self._render(
                lines,
                key.replace("_", " ").title(),
                value,
            )

        output_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return output_file

    def _render(self, lines, title, value, level=1):
        """
        Recursively render any JSON object into Markdown.
        """

        heading = "#" * level
        lines.append(f"{heading} {title}")
        lines.append("")

        if isinstance(value, dict):
            for k, v in value.items():
                self._render(lines, str(k).replace("_", " ").title(), v, level + 1)

        elif isinstance(value, list):
            if not value:
                lines.append("- None")
                lines.append("")
                return

            for item in value:
                if isinstance(item, (dict, list)):
                    self._render(lines, "", item, level + 1)
                else:
                    lines.append(f"- {item}")

            lines.append("")

        else:
            lines.append(str(value))
            lines.append("")


if __name__ == "__main__":

    from engines.weekly_dataset_builder import WeeklyDatasetBuilder
    from engines.weekly_json_writer import WeeklyJSONWriter

    print("=" * 70)
    print("TABELA WEEKLY MARKDOWN WRITER")
    print("=" * 70)

    dataset = WeeklyDatasetBuilder().build()
    json_file = WeeklyJSONWriter().write(dataset)
    output = WeeklyMarkdownWriter().write(json_file)

    print()
    print("Weekly Intelligence Markdown Generated")
    print(output)
    print()
