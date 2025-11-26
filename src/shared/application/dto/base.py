from abc import ABC
from pydantic import BaseModel, ConfigDict

class Base(BaseModel, ABC):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")
