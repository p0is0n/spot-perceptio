from shared.domain.aggregate.image import Image

from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

class DefaultPlateIdentifier(PlateIdentifier):
    async def identify(self, image: Image, /) -> Plate | None:
        return None
