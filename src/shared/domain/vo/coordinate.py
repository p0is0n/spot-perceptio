from __future__ import annotations

import math

from functools import cached_property
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

    @classmethod
    def from_xyxy(
        cls,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        /
    ) -> BoundingBox:
        if x1 > x2 or y1 > y2:
            raise ValueError(
                f"Invalid bbox coordinates: ({x1},{y1})-({x2},{y2})"
            )

        return cls(
            p1=Coordinate(x=x1, y=y1),
            p2=Coordinate(x=x2, y=y2),
        )

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

    def to_polygon(self) -> Polygon:
        return Polygon.from_bbox(self)


class RotatedBoundingBox(ValueObject):
    center: Coordinate
    width: NonNegativeInt
    height: NonNegativeInt
    angle: float = Field(description="Rotation angle in degrees, clockwise")

    @property
    def size(self) -> tuple[int, int]:
        return int(self.width), int(self.height)

    @property
    def radians(self) -> float:
        return math.radians(self.angle)

    @cached_property
    def x1(self) -> int:
        return self._xy1(0)

    @cached_property
    def y1(self) -> int:
        return self._xy1(1)

    @cached_property
    def x2(self) -> int:
        return self._xy2(0)

    @cached_property
    def y2(self) -> int:
        return self._xy2(1)

    def to_tuple(self) -> tuple[int, int, int, int]:
        return self.x1, self.y1, self.x2, self.y2

    def to_polygon(self) -> Polygon:
        return Polygon(
            corners=tuple(
                Coordinate(x=int(px), y=int(py))
                for px, py in self._corners
            )
        )

    @cached_property
    def _corners(self) -> tuple[tuple[float, float], ...]:
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

        return tuple(result)

    def _xy1(self, index: int) -> int:
        return math.floor(min(p[index] for p in self._corners))

    def _xy2(self, index: int) -> int:
        return math.ceil(max(p[index] for p in self._corners))


class Polygon(ValueObject):
    corners: tuple[Coordinate, ...] = Field(min_length=4)

    @classmethod
    def from_bbox(cls, box: BoundingBox, /) -> Polygon:
        return cls(corners=(
            Coordinate(x=box.x1, y=box.y1),
            Coordinate(x=box.x2, y=box.y1),
            Coordinate(x=box.x2, y=box.y2),
            Coordinate(x=box.x1, y=box.y2),
        ))

    @cached_property
    def x1(self) -> int:
        return min(int(c.x) for c in self.corners)

    @cached_property
    def y1(self) -> int:
        return min(int(c.y) for c in self.corners)

    @cached_property
    def x2(self) -> int:
        return max(int(c.x) for c in self.corners)

    @cached_property
    def y2(self) -> int:
        return max(int(c.y) for c in self.corners)

    def shift_by(self, other: Polygon) -> Polygon:
        dx = other.x1
        dy = other.y1

        corners = tuple(
            Coordinate(
                x=c.x + dx,
                y=c.y + dy
            )
            for c in self.corners
        )

        return Polygon(
            corners=corners
        )

    def expand(
        self,
        margin: int,
        bounds: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> Polygon:
        x1 = max(bounds.x1, self.x1 - margin)
        y1 = max(bounds.y1, self.y1 - margin)
        x2 = min(bounds.x2, self.x2 + margin)
        y2 = min(bounds.y2, self.y2 + margin)

        return Polygon.from_bbox(
            BoundingBox.from_xyxy(x1, y1, x2, y2)
        )

    def to_tuple_list(self) -> list[tuple[int, int]]:
        return [corner.to_tuple() for corner in self.corners]
