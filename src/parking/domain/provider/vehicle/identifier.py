from typing import Protocol

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from parking.domain.aggregate.vehicle import VehicleObserved

class VehicleIdentifier(Protocol):
    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None: ...
