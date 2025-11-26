from shared.domain.aggregate.image import Image

from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails
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

    async def recognize(self, image: Image, /) -> Vehicle | None:
        vehicle_details = await self._vehicle_identifier.identify(image)
        if vehicle_details is None:
            return None

        plate = await self._plate_identifier.identify(image)

        return self._make_vehicle(image, vehicle_details, plate)

    def _make_vehicle(
        self,
        image: Image,
        details: VehicleDetails,
        plate: Plate | None,
        /
    ) -> Vehicle:
        return Vehicle(
            image=image,
            details=details,
            plate=plate
        )
