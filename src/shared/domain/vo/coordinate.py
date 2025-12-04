import math

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

    def to_polygon(self) -> "Polygon":
        return Polygon(
            corners=(
                Coordinate(x=self.x1, y=self.y1),
                Coordinate(x=self.x2, y=self.y1),
                Coordinate(x=self.x2, y=self.y2),
                Coordinate(x=self.x1, y=self.y2),
            )
        )


class RotatedBoundingBox(ValueObject):
    center: Coordinate
    width: NonNegativeInt
    height: NonNegativeInt
    angle: float

    @property
    def size(self) -> tuple[int, int]:
        return int(self.width), int(self.height)

    @property
    def radians(self) -> float:
        return math.radians(self.angle)

    @property
    def x1(self) -> int:
        return self._xy1(0)

    @property
    def y1(self) -> int:
        return self._xy1(1)

    @property
    def x2(self) -> int:
        return self._xy2(0)

    @property
    def y2(self) -> int:
        return self._xy2(1)

    def to_tuple(self) -> tuple[int, int, int, int]:
        return self.x1, self.y1, self.x2, self.y2

    def to_polygon(self) -> "Polygon":
        return Polygon(
            corners=tuple(
                Coordinate(x=int(px), y=int(py))
                for px, py in self._corners
            )
        )

    @property
    def _corners(self) -> list[tuple[float, float]]:
        cx, cy = float(self.center.x), float(self.center.y)
        w, h = self.width / 2.0, self.height / 2.0

        cos_a = math.cos(self.radians)
        sin_a = math.sin(self.radians)

        local = [
            (-w, -h),
            ( w, -h),
            ( w,  h),
            (-w,  h)
        ]

        result = []
        for px, py in local:
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            result.append((rx, ry))

        return result

    def _xy1(self, index: int) -> int:
        return math.floor(min(p[index] for p in self._corners))

    def _xy2(self, index: int) -> int:
        return math.ceil(max(p[index] for p in self._corners))


class Polygon(ValueObject):
    corners: tuple[Coordinate, ...] = Field(min_length=4)

    @property
    def x1(self) -> int:
        return min(int(c.x) for c in self.corners)

    @property
    def y1(self) -> int:
        return min(int(c.y) for c in self.corners)

    @property
    def x2(self) -> int:
        return max(int(c.x) for c in self.corners)

    @property
    def y2(self) -> int:
        return max(int(c.y) for c in self.corners)

    def to_tuple_list(self) -> list[tuple[int, int]]:
        return [corner.to_tuple() for corner in self.corners]
