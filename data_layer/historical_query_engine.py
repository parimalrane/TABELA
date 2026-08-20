"""
===============================================================================
TABELA Historical Query Engine
===============================================================================

Purpose
-------
Single gateway to all historical TABELA data.

Version
-------
2.0

Status
------
Session 1 - Task 2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any


# =============================================================================
# DATASET STATUS
# =============================================================================

class DatasetStatus(Enum):
    FOUND = "FOUND"
    EMPTY = "EMPTY"
    MISSING = "MISSING"
    INVALID_JSON = "INVALID_JSON"


# =============================================================================
# DATASET
# =============================================================================

@dataclass(slots=True)
class Dataset:
    """
    Represents one dataset for one TABELA run.
    """

    name: str
    path: Path | None = None
    status: DatasetStatus = DatasetStatus.MISSING
    data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def exists(self) -> bool:
        return self.status in (
            DatasetStatus.FOUND,
            DatasetStatus.EMPTY,
        )


# =============================================================================
# RUN
# =============================================================================

@dataclass(slots=True)
class Run:
    """
    Represents one execution of TABELA.
    """

    date: date

    datasets: dict[str, Dataset] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, dataset_name: str) -> Dataset | None:
        return self.datasets.get(dataset_name)

    def has(self, dataset_name: str) -> bool:
        dataset = self.get(dataset_name)
        return dataset is not None and dataset.exists

    def list_datasets(self) -> list[str]:
        return sorted(self.datasets.keys())

    @property
    def is_complete(self) -> bool:
        """
        Complete means every registered dataset exists.
        Validation is performed later by HistoryBuilder.
        """
        return all(
            dataset.exists
            for dataset in self.datasets.values()
        )


# =============================================================================
# HISTORY
# =============================================================================

@dataclass(slots=True)
class History:
    """
    Historical database for all TABELA runs.
    """

    runs: list[Run] = field(default_factory=list)

    run_by_date: dict[date, Run] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    @property
    def latest_run(self) -> Run | None:
        if not self.runs:
            return None
        return self.runs[-1]

    @property
    def available_dates(self) -> list[date]:
        return [run.date for run in self.runs]

    @property
    def run_count(self) -> int:
        return len(self.runs)

    def get_run(self, run_date: date) -> Run | None:
        return self.run_by_date.get(run_date)

    def get_latest_run(self) -> Run | None:
        return self.latest_run

    def get_last_n_runs(self, n: int) -> list[Run]:
        if n <= 0:
            return []
        return self.runs[-n:]

    def get_runs_between(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Run]:

        return [
            run
            for run in self.runs
            if start_date <= run.date <= end_date
        ]

# =============================================================================
# IMPORTS
# =============================================================================

import re
from collections import defaultdict


# =============================================================================
# DATASET REGISTRY
# =============================================================================

class DatasetRegistry:
    """
    Central registry of all historical datasets.

    This is the ONLY place where dataset names and folders are defined.
    """

    MARKET_DATA = Path("market_data")

    DATASETS = {
        "snapshot": MARKET_DATA / "snapshots",
        "rotation_delta": MARKET_DATA / "rotation_delta",
        "stock_history": MARKET_DATA / "stock_universe",
        "watchlist": MARKET_DATA / "watchlist_history",
        "unknown": MARKET_DATA / "unknown_classification",
        "scanner": MARKET_DATA / "scanner_history",
    }

    @classmethod
    def dataset_names(cls) -> list[str]:
        return list(cls.DATASETS.keys())

    @classmethod
    def folder(cls, dataset_name: str) -> Path:
        return cls.DATASETS[dataset_name]

    @classmethod
    def folders(cls) -> dict[str, Path]:
        return cls.DATASETS.copy()


# =============================================================================
# FILE DISCOVERY
# =============================================================================

class FileDiscovery:
    """
    Discovers every historical TABELA run.

    Returns only file locations.

    Does NOT load JSON.
    """

    DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")

    def discover(self) -> dict[date, dict[str, Path]]:

        discovered: dict[date, dict[str, Path]] = defaultdict(dict)

        for dataset_name, folder in DatasetRegistry.folders().items():

            if not folder.exists():
                continue

            for file in sorted(folder.rglob("*.json")):

                run_date = self._extract_date(file.name)

                if run_date is None:
                    continue

                discovered[run_date][dataset_name] = file

        return dict(sorted(discovered.items()))

    @classmethod
    def _extract_date(cls, filename: str) -> date | None:

        match = cls.DATE_PATTERN.search(filename)

        if not match:
            return None

        try:
            return date.fromisoformat(match.group(1))

        except ValueError:
            return None

# =============================================================================
# IMPORTS
# =============================================================================

import json


# =============================================================================
# HISTORY BUILDER
# =============================================================================

class HistoryBuilder:
    """
    Builds the in-memory History object from discovered files.
    """

    def __init__(self):

        self.discovery = FileDiscovery()

    def build(self) -> History:

        history = History()

        discovered_runs = self.discovery.discover()

        for run_date, datasets in discovered_runs.items():

            run = Run(date=run_date)

            #
            # Create empty Dataset objects for every registered dataset.
            #

            for dataset_name in DatasetRegistry.dataset_names():

                run.datasets[dataset_name] = Dataset(
                    name=dataset_name
                )

            #
            # Populate datasets that were discovered.
            #

            for dataset_name, path in datasets.items():

                run.datasets[dataset_name] = self._load_dataset(
                    dataset_name,
                    path,
                )

            history.runs.append(run)

        history.runs.sort(key=lambda r: r.date)

        history.run_by_date = {
            run.date: run
            for run in history.runs
        }

        return history

    # ---------------------------------------------------------------------

    def _load_dataset(
        self,
        dataset_name: str,
        path: Path,
    ) -> Dataset:

        dataset = Dataset(
            name=dataset_name,
            path=path,
        )

        if not path.exists():

            dataset.status = DatasetStatus.MISSING

            return dataset

        try:

            with open(path, "r", encoding="utf-8") as f:

                data = json.load(f)

        except json.JSONDecodeError:

            dataset.status = DatasetStatus.INVALID_JSON

            return dataset

        except Exception:

            dataset.status = DatasetStatus.MISSING

            return dataset

        dataset.data = data

        if data in (None, {}, [], ""):

            dataset.status = DatasetStatus.EMPTY

        else:

            dataset.status = DatasetStatus.FOUND

        return dataset

# =============================================================================
# PUBLIC API
# =============================================================================

_ENGINE = None


def load_history(force_reload: bool = False) -> History:
    """
    Load historical data.

    History is cached after the first load.
    """

    global _ENGINE

    if _ENGINE is None or force_reload:

        _ENGINE = HistoryBuilder().build()

    return _ENGINE


def get_latest_run() -> Run | None:

    return load_history().latest_run


def get_run(run_date: date) -> Run | None:

    return load_history().get_run(run_date)


def get_last_n_runs(n: int) -> list[Run]:

    return load_history().get_last_n_runs(n)


def get_runs_between(
    start_date: date,
    end_date: date,
) -> list[Run]:

    return load_history().get_runs_between(
        start_date,
        end_date,
    )


if __name__ == "__main__":

    history = load_history()

    print("=" * 70)
    print("TABELA HISTORICAL QUERY ENGINE")
    print("=" * 70)

    print(f"Runs Loaded : {history.run_count}")
    print(f"Latest Run  : {history.latest_run.date}")
    print()

    latest = get_latest_run()

    print("Latest Run Datasets")
    print("-" * 70)

    for dataset in latest.datasets.values():

        print(
            f"{dataset.name:<20}"
            f"{dataset.status.value:<15}"
            f"{dataset.path.name if dataset.path else '---'}"
        )

    print()

    print("Last 5 Runs")
    print("-" * 70)

    for run in get_last_n_runs(5):

        loaded = sum(
            d.status == DatasetStatus.FOUND
            for d in run.datasets.values()
        )

        print(
            f"{run.date}   "
            f"{loaded}/{len(run.datasets)} datasets loaded"
        )

