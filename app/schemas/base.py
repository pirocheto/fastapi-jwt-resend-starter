from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel):
    status: str
    code: str
    message: str


class DataAPIResponse(APIResponse, Generic[T]):
    data: T | None = None
