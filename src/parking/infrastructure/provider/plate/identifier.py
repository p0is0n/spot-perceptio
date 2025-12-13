from shared.domain.aggregate.image import Image

from shared.domain.vo.coordinate import Polygon
from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

class DefaultPlateIdentifier(PlateIdentifier):
    def __init__(self, identifiers: tuple[PlateIdentifier, ...], /) -> None:
        self._identifiers = identifiers

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        plate: Plate | None = None
        for identifier in self._identifiers:
            plate = await identifier.identify(image, vehicle_coordinate)
            if plate is not None:
                return plate

        return None
