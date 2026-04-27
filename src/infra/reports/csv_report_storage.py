import csv
from pathlib import Path

from application.reports.report_storage import ReportStorage


class CsvReportStorage(ReportStorage):
    def __init__(self, storage_dir: str):
        self._storage_dir = Path(storage_dir)

    def save(self, filename: str, rows: list[dict], fieldnames: list[str]) -> None:
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        path = self._storage_dir / filename
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
