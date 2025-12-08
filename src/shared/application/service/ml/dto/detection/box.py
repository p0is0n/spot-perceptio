from enum import Enum

from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox
from shared.application.dto.base import Base

class Type(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    TRUCK = "truck"
    BUS = "bus"
    VAN = "van"
    LICENSE_PLATE = "license_plate"
    UNKNOWN = "unknown"


class Box(Base):
    type: Type
    score: float
    coordinate: BoundingBox | RotatedBoundingBox
