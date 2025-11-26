from shared.domain.aggregate.base import Aggregate
from shared.domain.aggregate.image import Image

from parking.domain.vo.plate import Plate
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType

class VehicleDetails(Aggregate):
    type: VehicleType
    color: Color


class Vehicle(Aggregate):
    image: Image
    details: VehicleDetails
    plate: Plate | None = None
