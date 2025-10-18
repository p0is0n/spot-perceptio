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

    async def analyze(self, image: Image, spot: Spot) -> ParkingSpot:
        vehicle_image = image.crop(spot.coordinate)
        vehicle = await self._vehicle_recognizer.recognize(vehicle_image)
        if vehicle is not None:
            return self._make_parking_spot(spot, vehicle)

        return self._make_empty_parking_spot(spot)

    def _make_parking_spot(
        self,
        spot: Spot,
        vehicle: Vehicle | None = None
    ) -> ParkingSpot:
        occupied = vehicle is not None

        return ParkingSpot(
            occupied=occupied,
            spot=spot,
            vehicle=vehicle
        )

    def _make_empty_parking_spot(self, spot: Spot) -> ParkingSpot:
        return self._make_parking_spot(spot)
