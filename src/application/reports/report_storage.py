from abc import ABC, abstractmethod


class ReportStorage(ABC):
    @abstractmethod
    def save(self, filename: str, rows: list[dict], fieldnames: list[str]) -> None:
        """Сохраняет набор строк как отчёт с заданным именем файла."""
        raise NotImplementedError
