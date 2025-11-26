from shared.domain.aggregate.base import Aggregate
from shared.domain.aggregate.spot import Spot
from parking.domain.aggregate.vehicle import Vehicle

class ParkingSpot(Aggregate):
    occupied: bool
    spot: Spot
    vehicle: Vehicle | None = None
