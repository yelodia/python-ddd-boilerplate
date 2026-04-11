import json
from abc import ABC
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel


class Table(BaseModel):
    # аналог таблицы в реляционной БД, потому что где-то
    # нужно хранить автоинкрементальный счётчик
    auto_increment_id: int = 0
    data: list[dict[str, Any]] = []


class JsonRepositoryBase(ABC):
    _path: Path

    @staticmethod
    def _create_if_not_exists(path: str | Path) -> None:
        # если файла нет, то создаем его с начальной структурой
        path: Path = path if isinstance(path, Path) else Path(path)

        if not path.exists():
            initial_table = Table()
            with open(path, mode="w", encoding="utf-8") as f:
                json.dump(initial_table.model_dump(mode='json'), f, indent=2, ensure_ascii=False)

    async def _load(self) -> Table:
        async with aiofiles.open(self._path, mode="r", encoding="utf-8") as f:
            result = json.loads(await f.read())
            return Table.model_validate(result)

    async def _save(self, table: Table) -> None:
        content = json.dumps(table.model_dump(mode='json'), indent=2, ensure_ascii=False, default=str)
        async with aiofiles.open(self._path, mode="w", encoding="utf-8") as f:
            await f.write(content)
