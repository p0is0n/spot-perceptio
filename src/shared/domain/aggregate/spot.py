from dataclasses import dataclass

from shared.domain.vo.base import Id
from shared.domain.vo.coordinate import BoundingBox

@dataclass(frozen=True)
class Spot:
    id: Id
    coordinate: BoundingBox
