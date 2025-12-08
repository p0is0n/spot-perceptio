from shared.application.dto.base import Base

from parking.application.dto.contract.coordinate import Polygon
from parking.application.dto.contract.plate import Plate

class VehicleDetails(Base):
    type: str
    color: str


class Vehicle(Base):
    details: VehicleDetails
    plate: Plate | None = None
    coordinate: Polygon
