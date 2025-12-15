from pydantic import Field

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.base import Aggregate

from parking.domain.vo.plate import Plate
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType

class VehicleDetails(Aggregate):
    type: VehicleType
    color: Color


class VehicleObserved(Aggregate):
    details: VehicleDetails
    coordinate: Polygon
    score: float = Field(gt=0.0, lt=1.0)


class Vehicle(Aggregate):
    details: VehicleDetails
    plate: Plate | None = None
    coordinate: Polygon
