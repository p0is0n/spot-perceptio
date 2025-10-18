from dataclasses import dataclass

from shared.domain.aggregate.image import Image

from parking.domain.vo.plate import Plate
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType

@dataclass(frozen=True)
class VehicleDetails:
    type: VehicleType
    color: Color


@dataclass(frozen=True)
class Vehicle:
    image: Image
    details: VehicleDetails
    plate: Plate | None = None
