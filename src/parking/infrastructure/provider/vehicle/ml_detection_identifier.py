from shared.domain.aggregate.image import Image
from shared.application.service.ml.provider.detection import MLDetectionProvider
from shared.application.service.ml.dto import detection

from parking.domain.aggregate.vehicle import VehicleDetails
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class MLDetectionVehicleIdentifier(VehicleIdentifier):
    _source_imgsz: int = 640
    _score_threshold: float = 0.70

    def __init__(self, provider: MLDetectionProvider, /) -> None:
        self._provider = provider

    async def identify(self, image: Image, /) -> VehicleDetails | None:
        response = await self._provider.predict(detection.Request(
            source=image
        ))
        result = await self._process_response(response)

        return result

    async def _process_response(self, response: detection.Response) -> VehicleDetails | None:
        if len(response.boxes) == 0:
            return None

        results: list[detection.Box] = []
        for box in response.boxes:
            if box.score < self._score_threshold:
                continue

            results.append(box)
            if len(results) > 1:
                raise ValueError("Multiple vehicle detections found.")

        if len(results) == 1:
            result = results[0]

            return VehicleDetails(
                type=VehicleType(result.type.value),
                color=Color.UNKNOWN
            )

        return None
