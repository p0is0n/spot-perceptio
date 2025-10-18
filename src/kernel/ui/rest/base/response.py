from typing import TypeVar, Generic
from pydantic import BaseModel

ResultT = TypeVar("ResultT")


class BaseResponse(BaseModel, Generic[ResultT]):
    data: ResultT
