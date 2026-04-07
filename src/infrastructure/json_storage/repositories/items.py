import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import aiofiles

from core.items.exceptions import ItemNotFoundError
# from infrastructure.bootstrap import register_repo, JSON, Registration
from src.core.items.entities import Item
from src.core.items.repository import ItemRepository
from dataclasses import asdict


# TODO вероятно, стоит завести какие-то местные модельки на будущее,
#  чтобы изменения в сущностях не приводили к слому структуры хранимых данных.
#  В первую очередь касается методов create и update, но пока что так сойдет.

class JsonItemRepository(ItemRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.path = Path(data_dir) / "items.json"

    async def get_by_id(self, item_id: UUID) -> Item:
        item_id = str(item_id)
        item = next((i for i in await self._load() if i["id"] == item_id), None)
        if not item:
            raise ItemNotFoundError(f"Item with ID {item_id} not found")
        return self._to_domain(item)

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[Item]:
        return [self._to_domain(i) for i in (await self._load())[offset: offset + limit]]

    async def create(self, item: Item) -> None:
        record = asdict(item)
        items = await self._load()
        # TODO должна ли вылетать ошибка ItemAlreadyExistsError(f"Item with ID {item.id} already exists")?
        items.append(record)
        await self._save(items)

    async def update(self, item: Item) -> None:
        items = await self._load()
        for i, record in enumerate(items):
            if record["id"] == item.id:
                items[i] = {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "is_active": item.is_active,
                    "created_at": item.created_at.isoformat(),
                }
                break
        await self._save(items)

    async def delete(self, item_id: UUID) -> None:
        items = [i for i in await self._load() if i["id"] != item_id]
        await self._save(items)

    @staticmethod
    def _to_domain(record: dict) -> Item:
        return Item(
            id=record["id"],
            title=record["title"],
            description=record.get("description"),
            is_active=record.get("is_active", True),
            created_at=datetime.fromisoformat(record["created_at"]),
        )

    async def _load(self) -> list[dict]:
        async with aiofiles.open(self.path, encoding="utf-8") as f:
            result: list[dict] = json.loads(await f.read())
            return result

    async def _save(self, items: list[dict]) -> None:
        content = json.dumps(items, indent=2, ensure_ascii=False, default=str)
        async with aiofiles.open(self.path, "w", encoding="utf-8") as f:
            await f.write(content)


# Registration.register_repo(JSON, ItemRepository, JsonItemRepository)
