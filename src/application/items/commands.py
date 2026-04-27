from uuid import UUID

from pydantic import BaseModel, Field


class ShowAllItemsCmd(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class GetItemCmd(BaseModel):
    item_id: UUID


class CreateItemCmd(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class UpdateItemCmd(BaseModel):
    item_id: UUID
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class DeleteItemCmd(BaseModel):
    item_id: UUID
