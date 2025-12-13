from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox
from shared.application.dto.base import Base

class Type(Base):
    id: int
    name: str


class Box(Base):
    type: Type
    score: float
    coordinate: BoundingBox | RotatedBoundingBox
