from engines.weekly_dataset_builder import WeeklyDatasetBuilder
from engines.weekly_json_writer import WeeklyJSONWriter


if __name__ == "__main__":

    print("=" * 70)
    print("TABELA WEEKLY INTELLIGENCE")
    print("=" * 70)

    dataset = WeeklyDatasetBuilder().build()

    output = WeeklyJSONWriter().write(dataset)

    print()
    print(f"Weekly JSON saved to:")
    print(output)
    print()