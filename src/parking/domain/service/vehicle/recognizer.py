from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from parking.domain.aggregate.vehicle import Vehicle, VehicleObserved
from parking.domain.vo.plate import Plate
from parking.domain.provider.vehicle.identifier import VehicleIdentifier
from parking.domain.provider.plate.identifier import PlateIdentifier

class VehicleRecognizer:
    def __init__(
        self,
        vehicle_identifier: VehicleIdentifier,
        plate_identifier: PlateIdentifier
    ) -> None:
        self._vehicle_identifier = vehicle_identifier
        self._plate_identifier = plate_identifier

    async def recognize(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> Vehicle | None:
        vehicle_observed = await self._vehicle_identifier.identify(image, spot_coordinate)
        if vehicle_observed is None:
            return None

        plate = await self._plate_identifier.identify(
            image,
            vehicle_observed.coordinate
        )

        return self._make_vehicle(image, vehicle_observed, plate)

    def _make_vehicle(
        self,
        image: Image,
        observed: VehicleObserved,
        plate: Plate | None,
        /
    ) -> Vehicle:
        return Vehicle(
            image=image,
            details=observed.details,
            plate=plate,
            coordinate=observed.coordinate
        )
