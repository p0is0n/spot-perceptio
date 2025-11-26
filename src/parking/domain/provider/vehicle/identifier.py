from typing import Protocol

from shared.domain.aggregate.image import Image
from parking.domain.aggregate.vehicle import VehicleDetails

class VehicleIdentifier(Protocol):
    async def identify(self, image: Image, /) -> VehicleDetails | None: ...
