import os

os.environ.setdefault("STORAGE_BACKEND", "json")
os.environ.setdefault("JSON_DATA_DIR", "data/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import pytest

from src.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()
