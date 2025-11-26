from pydantic import NonNegativeInt

from shared.application.dto.base import Base

class Coordinate(Base):
    x: NonNegativeInt
    y: NonNegativeInt


class BoundingBox(Base):
    p1: Coordinate
    p2: Coordinate

class Polygon(Base):
    corners: tuple[Coordinate, ...]
