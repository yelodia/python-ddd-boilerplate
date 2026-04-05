import json
from datetime import datetime
from pathlib import Path

import aiofiles

from src.core.items.entities import ItemData
from src.core.items.repository import AbstractItemRepository


class JsonItemRepository(AbstractItemRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.path = Path(data_dir) / "items.json"

    async def get_by_id(self, item_id: int) -> ItemData | None:
        found = next((i for i in await self._load() if i["id"] == item_id), None)
        return self._to_domain(found) if found else None

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ItemData]:
        return [self._to_domain(i) for i in (await self._load())[offset : offset + limit]]

    async def create(self, title: str, description: str | None) -> ItemData:
        items = await self._load()
        new_id = max((i["id"] for i in items), default=0) + 1
        record = {
            "id": new_id,
            "title": title,
            "description": description,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
        items.append(record)
        await self._save(items)
        return self._to_domain(record)

    async def update(self, item: ItemData) -> ItemData:
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
        return item

    async def delete(self, item_id: int) -> None:
        items = [i for i in await self._load() if i["id"] != item_id]
        await self._save(items)

    def _to_domain(self, record: dict) -> ItemData:
        return ItemData(
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
