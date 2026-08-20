"""
===============================================================================
TABELA Historical Queries
===============================================================================

Reusable query functions built on top of the Historical Query Engine.

This module NEVER reads JSON files directly.
"""

from __future__ import annotations

from datetime import date

from data_layer.historical_query_engine import (
    History,
    Run,
    Dataset,
)

from data_layer.historical_query_engine import DatasetStatus


class HistoricalQueries:

    def __init__(self, history: History):

        self.history = history

    def latest_run(self) -> Run | None:

        return self.history.latest_run

    def first_run(self) -> Run | None:

        if not self.history.runs:
            return None

        return self.history.runs[0]

    def total_runs(self) -> int:

        return self.history.run_count

    def available_dates(self) -> list[date]:

        return self.history.available_dates
    

    # ------------------------------------------------------------------
    # Dataset Queries
    # ------------------------------------------------------------------

    def dataset(self, run: Run, dataset_name: str) -> Dataset | None:
        """
        Return a dataset from a specific run.
        """
        return run.get(dataset_name)

    def latest_dataset(self, dataset_name: str) -> Dataset | None:
        """
        Return the latest available dataset.
        """
        latest = self.latest_run()

        if latest is None:
            return None

        return latest.get(dataset_name)

    def datasets(self, dataset_name: str) -> list[Dataset]:
        """
        Return all datasets of a given type.
        """

        result = []

        for run in self.history.runs:

            dataset = run.get(dataset_name)

            if dataset is not None:

                result.append(dataset)

        return result

    def latest_available_dataset(self, dataset_name: str) -> Dataset | None:
        """
        Return the most recent FOUND dataset.
        """

        for run in reversed(self.history.runs):

            dataset = run.get(dataset_name)

            if (
                dataset is not None
                and dataset.status == DatasetStatus.FOUND
            ):
                return dataset

        return None



    # ------------------------------------------------------------------
    # Run Queries
    # ------------------------------------------------------------------

    def previous_run(self, run: Run) -> Run | None:
        """
        Return the previous available run.
        """

        try:
            index = self.history.runs.index(run)
        except ValueError:
            return None

        if index == 0:
            return None

        return self.history.runs[index - 1]


    def next_run(self, run: Run) -> Run | None:
        """
        Return the next available run.
        """

        try:
            index = self.history.runs.index(run)
        except ValueError:
            return None

        if index >= len(self.history.runs) - 1:
            return None

        return self.history.runs[index + 1]


    def latest_n_runs(self, n: int) -> list[Run]:

        return self.history.get_last_n_runs(n)


    def run_exists(self, run_date: date) -> bool:

        return self.history.get_run(run_date) is not None
    

    # ------------------------------------------------------------------
    # Time Queries
    # ------------------------------------------------------------------

    def runs_between(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Run]:
        """
        Return runs between two dates (inclusive).
        """
        return self.history.get_runs_between(start_date, end_date)

    def runs_after(self, start_date: date) -> list[Run]:
        """
        Return runs on or after the specified date.
        """
        return [
            run
            for run in self.history.runs
            if run.date >= start_date
        ]

    def runs_before(self, end_date: date) -> list[Run]:
        """
        Return runs on or before the specified date.
        """
        return [
            run
            for run in self.history.runs
            if run.date <= end_date
        ]

    def latest_date(self) -> date | None:
        """
        Return the latest available run date.
        """
        latest = self.latest_run()
        return latest.date if latest else None

    def first_date(self) -> date | None:
        """
        Return the first available run date.
        """
        first = self.first_run()
        return first.date if first else None
    


if __name__ == "__main__":

    from historical_query_engine import (
        load_history,
        DatasetStatus,
    )

    history = load_history()

    q = HistoricalQueries(history)

    print("=" * 70)
    print("TABELA HISTORICAL QUERIES")
    print("=" * 70)

    assert q.total_runs() == history.run_count

    assert q.latest_run() is not None

    assert q.first_run() is not None

    assert q.latest_date() >= q.first_date()

    assert q.previous_run(q.latest_run()) is not None

    snapshot = q.latest_dataset("snapshot")

    assert snapshot is not None

    assert snapshot.status == DatasetStatus.FOUND

    snapshots = q.datasets("snapshot")

    assert len(snapshots) == history.run_count

    latest_snapshot = q.latest_available_dataset("snapshot")

    assert latest_snapshot is not None

    print("All validation tests passed.")


