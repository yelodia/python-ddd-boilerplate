import json
from datetime import datetime
from pathlib import Path

import aiofiles

from src.auth.domain import UserData
from src.auth.repository.abstract import AbstractUserRepository
from src.auth.schemas import UserCreate


class JsonUserRepository(AbstractUserRepository):
    def __init__(self, data_dir: str = "data") -> None:
        self.path = Path(data_dir) / "users.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    async def get_by_id(self, user_id: int) -> UserData | None:
        found = next((u for u in await self._load() if u["id"] == user_id), None)
        return self._to_domain(found) if found else None

    async def get_by_email(self, email: str) -> UserData | None:
        found = next((u for u in await self._load() if u["email"] == email), None)
        return self._to_domain(found) if found else None

    async def create(self, data: UserCreate, hashed_password: str) -> UserData:
        users = await self._load()
        new_id = max((u["id"] for u in users), default=0) + 1
        record = {
            "id": new_id,
            "email": data.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
        users.append(record)
        await self._save(users)
        return self._to_domain(record)

    def _to_domain(self, record: dict) -> UserData:
        return UserData(
            id=record["id"],
            email=record["email"],
            is_active=record.get("is_active", True),
            created_at=datetime.fromisoformat(record["created_at"]),
        )

    async def _load(self) -> list[dict]:
        async with aiofiles.open(self.path, encoding="utf-8") as f:
            result: list[dict] = json.loads(await f.read())
            return result

    async def _save(self, users: list[dict]) -> None:
        content = json.dumps(users, indent=2, ensure_ascii=False, default=str)
        async with aiofiles.open(self.path, "w", encoding="utf-8") as f:
            await f.write(content)
