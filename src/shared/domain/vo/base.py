from abc import ABC
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from pydantic.types import StringConstraints

class ValueObject(BaseModel, ABC):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")


class Id(ValueObject):
    value: Annotated[str, StringConstraints(min_length=1)]
