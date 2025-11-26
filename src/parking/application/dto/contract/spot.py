from shared.application.dto.base import Base

from parking.application.dto.contract.coordinate import Polygon
from parking.application.dto.contract.vehicle import Vehicle

class Spot(Base):
    id: str
    coordinate: Polygon


class ParkingSpot(Base):
    occupied: bool
    spot: Spot
    vehicle: Vehicle | None = None
