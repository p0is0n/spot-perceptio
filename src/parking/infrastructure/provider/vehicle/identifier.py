from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from parking.domain.aggregate.vehicle import VehicleObserved
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class DefaultVehicleIdentifier(VehicleIdentifier):
    async def identify(
        self,
        image: Image,
        coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        return None
