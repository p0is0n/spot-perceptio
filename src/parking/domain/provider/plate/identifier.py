from typing import Protocol

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from parking.domain.vo.plate import Plate

class PlateIdentifier(Protocol):
    async def identify(
        self,
        image: Image,
        coordinate: Polygon,
        /
    ) -> Plate | None: ...
