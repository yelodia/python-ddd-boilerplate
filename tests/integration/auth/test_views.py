from httpx import AsyncClient


async def test_get_user_not_found(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/99999")
    assert resp.status_code == 404
