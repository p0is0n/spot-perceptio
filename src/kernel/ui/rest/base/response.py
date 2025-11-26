from typing import TypeVar, Generic
from pydantic import BaseModel, ConfigDict

ResultT = TypeVar("ResultT")

class BaseResponse(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")


class Response(BaseResponse, Generic[ResultT]):
    data: ResultT
