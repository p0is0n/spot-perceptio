from dataclasses import dataclass

from shared.domain.aggregate.spot import Spot
from parking.domain.aggregate.vehicle import Vehicle

@dataclass(frozen=True)
class ParkingSpot:
    occupied: bool
    spot: Spot
    vehicle: Vehicle | None = None
