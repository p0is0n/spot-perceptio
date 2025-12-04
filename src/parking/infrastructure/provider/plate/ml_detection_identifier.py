from shared.domain.aggregate.image import Image

from shared.domain.vo.coordinate import Polygon
from shared.application.service.ml.provider.detection import MlDetectionProvider

from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

class MlDetectionPlateIdentifier(PlateIdentifier):
    def __init__(
        self,
        provider: MlDetectionProvider,
        threshold: float,
        /
    ) -> None:
        self._provider = provider
        self._threshold = threshold

    async def identify(
        self,
        image: Image,
        coordinate: Polygon,
        /
    ) -> Plate | None:
        return None
