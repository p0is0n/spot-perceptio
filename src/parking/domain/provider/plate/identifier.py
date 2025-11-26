from typing import Protocol

from shared.domain.aggregate.image import Image
from parking.domain.vo.plate import Plate

class PlateIdentifier(Protocol):
    async def identify(self, image: Image, /) -> Plate | None: ...
