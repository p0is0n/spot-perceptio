from shared.domain.aggregate.image import Image
from shared.domain.aggregate.spot import Spot

from parking.domain.aggregate.spot import ParkingSpot
from parking.domain.aggregate.vehicle import Vehicle
from parking.domain.service.vehicle.recognizer import VehicleRecognizer

class SpotAnalyzer:
    def __init__(
        self,
        vehicle_recognizer: VehicleRecognizer
    ) -> None:
        self._vehicle_recognizer = vehicle_recognizer

    async def analyze(self, image: Image, spot: Spot, /) -> ParkingSpot:
        vehicle = await self._vehicle_recognizer.recognize(
            image,
            spot.coordinate
        )

        return self._make_parking_spot(spot, vehicle)

    def _make_parking_spot(
        self,
        spot: Spot,
        vehicle: Vehicle | None,
        /
    ) -> ParkingSpot:
        occupied: bool = vehicle is not None

        return ParkingSpot(
            occupied=occupied,
            spot=spot,
            vehicle=vehicle
        )
