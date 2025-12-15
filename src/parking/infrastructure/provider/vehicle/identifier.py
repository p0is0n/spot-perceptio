from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from parking.domain.aggregate.vehicle import VehicleObserved
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class DefaultVehicleIdentifier(VehicleIdentifier):
    def __init__(self, identifiers: tuple[VehicleIdentifier, ...], /) -> None:
        self._identifiers = identifiers

    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        vehicle_observed: VehicleObserved | None = None
        for identifier in self._identifiers:
            vehicle_observed = await identifier.identify(image, spot_coordinate)
            if vehicle_observed is not None:
                return vehicle_observed

        return None
