import os
import shutil
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from config import get_settings
from infra.storage.json.setup import ensure_json_storage
from main import create_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    settings = get_settings()
    if settings.use_json_storage:
        ensure_json_storage(settings.json_data_dir)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    if os.path.exists(settings.json_data_dir):
        shutil.rmtree(settings.json_data_dir)
