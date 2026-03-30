import json
from datetime import datetime
from pathlib import Path

import aiofiles

from src.items.domain import ItemData
from src.items.repository.abstract import AbstractItemRepository
from src.items.schemas import ItemCreate


class JsonItemRepository(AbstractItemRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.path = Path(data_dir) / "items.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    async def get_by_id(self, item_id: int) -> ItemData | None:
        found = next((i for i in await self._load() if i["id"] == item_id), None)
        return self._to_domain(found) if found else None

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ItemData]:
        return [self._to_domain(i) for i in (await self._load())[offset : offset + limit]]

    async def create(self, data: ItemCreate) -> ItemData:
        items = await self._load()
        new_id = max((i["id"] for i in items), default=0) + 1
        record = {
            "id": new_id,
            **data.model_dump(),
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
        items.append(record)
        await self._save(items)
        return self._to_domain(record)

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
