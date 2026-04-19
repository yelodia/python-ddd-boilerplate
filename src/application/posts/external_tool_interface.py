from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class PostDTO(BaseModel):
    id: str
    image_url: str
    likes: int
    created_at: datetime
    text: str


class PostsResponseDTO(BaseModel):
    total: int
    posts: list[PostDTO]


class ExternalToolApiClient(ABC):
    @abstractmethod
    async def get_posts(self, page: int, limit: int) -> PostsResponseDTO:
        raise NotImplementedError
