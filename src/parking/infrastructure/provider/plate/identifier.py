from shared.domain.aggregate.image import Image

from shared.domain.vo.coordinate import Polygon
from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

class DefaultPlateIdentifier(PlateIdentifier):
    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        return None
