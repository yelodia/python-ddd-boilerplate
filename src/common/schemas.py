from pydantic import BaseModel


class PagedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
