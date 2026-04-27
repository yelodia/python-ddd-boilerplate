from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_list_items_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/items/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_and_get_item(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/items/",
        json={"title": "Test Item", "description": "desc"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Item"
    item_id = data["id"]

    resp = await client.get(f"/api/v1/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id


async def test_delete_item(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/items/",
        json={"title": "To Delete"},
    )
    item_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/items/{item_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/items/{item_id}")
    assert resp.status_code == 404


async def test_update_item(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/items/",
        json={"title": "Original", "description": "old"},
    )
    item_id = resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/items/{item_id}",
        json={"title": "Updated", "description": "new"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated"
    assert data["description"] == "new"


async def test_update_item_not_found(client: AsyncClient) -> None:
    resp = await client.patch("/api/v1/items/99999", json={"title": "X"})
    assert resp.status_code == 404


async def test_get_item_not_found(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/items/99999")
    assert resp.status_code == 404
