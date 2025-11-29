from shared.domain.aggregate.image import Image
from shared.application.service.ml.provider.detection import MlDetectionProvider
from shared.application.service.ml.dto import detection

from parking.domain.aggregate.vehicle import VehicleDetails
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class MlDetectionVehicleIdentifier(VehicleIdentifier):
    _imgsz: int = 640
    _threshold: float

    def __init__(
        self,
        provider: MlDetectionProvider,
        threshold: float,
        /
    ) -> None:
        self._provider = provider
        self._threshold = threshold

    async def identify(self, image: Image, /) -> VehicleDetails | None:
        response = await self._provider.predict(detection.Request(
            source=image
        ))
        result = await self._process_response(response)

        return result

    async def _process_response(self, response: detection.Response) -> VehicleDetails | None:
        if len(response.boxes) == 0:
            return None

        vehicles: list[VehicleDetails] = []
        for box in response.boxes:
            if box.score < self._threshold:
                continue

            vehicle = VehicleDetails(
                type=VehicleType(box.type.value),
                color=Color.UNKNOWN
            )
            if vehicle.type == VehicleType.UNKNOWN:
                continue

            vehicles.append(vehicle)
            if len(vehicles) > 1:
                raise ValueError("Multiple vehicle detections found.")

        if len(vehicles) == 1:
            return vehicles[0]

        return None
