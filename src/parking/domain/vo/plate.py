from typing import Annotated
from pydantic.types import StringConstraints

from shared.domain.vo.base import ValueObject

class Plate(ValueObject):
    value: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    country: Annotated[str, StringConstraints(min_length=2, max_length=2)]
