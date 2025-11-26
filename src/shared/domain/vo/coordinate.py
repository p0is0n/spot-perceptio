from pydantic import NonNegativeInt, Field
from shared.domain.vo.base import ValueObject

class Coordinate(ValueObject):
    x: NonNegativeInt
    y: NonNegativeInt

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y


class BoundingBox(ValueObject):
    p1: Coordinate
    p2: Coordinate

    @property
    def x1(self) -> int:
        return min(self.p1.x, self.p2.x)

    @property
    def y1(self) -> int:
        return min(self.p1.y, self.p2.y)

    @property
    def x2(self) -> int:
        return max(self.p1.x, self.p2.x)

    @property
    def y2(self) -> int:
        return max(self.p1.y, self.p2.y)

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        return self.width * self.height

    def to_tuple(self) -> tuple[int, int, int, int]:
        return self.x1, self.y1, self.x2, self.y2


class RotatedBoundingBox(ValueObject):
    center: Coordinate
    width: NonNegativeInt
    height: NonNegativeInt
    angle: float

    @property
    def size(self) -> tuple[int, int]:
        return int(self.width), int(self.height)


class Polygon(ValueObject):
    corners: tuple[Coordinate, ...] = Field(min_length=4)

    def to_tuple_list(self) -> list[tuple[int, int]]:
        return [corner.to_tuple() for corner in self.corners]
