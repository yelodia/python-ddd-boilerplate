from datetime import datetime

from pydantic import BaseModel


class Post(BaseModel):
    id: str
    image_url: str
    likes: int
    created_at: datetime
    text: str


class PostsResponse(BaseModel):
    page: int
    per_page: int
    total: int
    posts: list[Post]
