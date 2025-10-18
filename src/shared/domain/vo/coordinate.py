from dataclasses import dataclass
from shared.domain.vo.base import ValueObject
from shared.domain.exception.base import ValidationError

@dataclass(frozen=True)
class Coordinate(ValueObject):
    x: float
    y: float


@dataclass(frozen=True)
class BoundingBox(ValueObject):
    p1: Coordinate
    p2: Coordinate

    def __post_init__(self):
        if self.p1.x > self.p2.x or self.p1.y > self.p2.y:
            raise ValidationError("Coordinates are not valid.")

    @property
    def width(self) -> float:
        return abs(self.p2.x - self.p1.x)

    @property
    def height(self) -> float:
        return abs(self.p2.y - self.p1.y)

    @property
    def area(self) -> float:
        return self.width * self.height
