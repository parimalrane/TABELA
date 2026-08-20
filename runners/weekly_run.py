import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.weekly_pipeline import WeeklyIntelligenceEngine
from reporting.weekly_json_writer import WeeklyJSONWriter


if __name__ == "__main__":

    print("=" * 70)
    print("TABELA WEEKLY INTELLIGENCE")
    print("=" * 70)

    report = WeeklyIntelligenceEngine().build()

    output = WeeklyJSONWriter().write(report.dataset)

    print()
    print(f"Weekly JSON saved to:")
    print(output)
    print()