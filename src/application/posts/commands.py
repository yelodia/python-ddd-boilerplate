from pydantic import BaseModel


class RequestPostCmd(BaseModel):
    page: int
    limit: int
