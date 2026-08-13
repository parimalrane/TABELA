from core.weekly_pipeline import WeeklyIntelligenceEngine
from engines.weekly_json_writer import WeeklyJSONWriter


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