import httpx

from application.posts.external_tool_interface import ExternalToolApiClient, PostDTO, PostsResponseDTO


class DummyApiClient(ExternalToolApiClient):
    def __init__(self, base_url: str, app_id: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"app-id": app_id},
            timeout=10.0,
        )

    async def get_posts(self, page: int, limit: int) -> PostsResponseDTO:
        if page is None:
            raise ValueError("Page number must be provided")

        if page < 0:
            raise ValueError("Page number must be >= 0")

        if limit is None:
            raise ValueError("Limit must be provided")

        if limit <= 0:
            raise ValueError("Limit must be > 0")

        response = await self._client.get("/post", params={"page": page, "limit": limit})
        response.raise_for_status()

        raw_data = response.json()

        return PostsResponseDTO(
            total=raw_data["total"],
            posts=[
                PostDTO(
                    id=item["id"],
                    image_url=item["image"],
                    likes=item["likes"],
                    created_at=item["publishDate"],
                    text=item["text"],
                )
                for item in raw_data["data"]
            ],
        )
