import os

os.environ.setdefault("STORAGE_BACKEND", "json")
os.environ.setdefault("JSON_DATA_DIR", "data/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import shutil
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from src.config import get_settings
from src.main import create_app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    test_data_dir = get_settings().json_data_dir
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
