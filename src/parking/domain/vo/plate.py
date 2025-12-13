from typing import Annotated
from pydantic.types import StringConstraints

from shared.domain.vo.base import ValueObject
from shared.domain.vo.coordinate import Polygon
from shared.domain.enum.country import Country

class Plate(ValueObject):
    value: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    country: Country
    coordinate: Polygon
