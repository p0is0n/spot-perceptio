import cv2
import numpy as np

from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox, Polygon
from shared.domain.aggregate.image import Image
from shared.application.service.ml.provider.detection import MlDetectionProvider
from shared.application.service.ml.dto import detection

from parking.domain.aggregate.vehicle import VehicleDetails, VehicleObserved
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

    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        response = await self._provider.predict(detection.Request(
            source=image,
            image_size=self._imgsz
        ))
        result = await self._process_response(spot_coordinate, response)

        return result

    async def _process_response(
        self,
        coordinate: Polygon,
        response: detection.Response,
        /
    ) -> VehicleObserved | None:
        if len(response.boxes) == 0:
            return None

        vehicles: list[VehicleObserved] = []
        for box in response.boxes:
            if box.score < self._threshold:
                continue

            if not self._box_in_coordinate(box, coordinate):
                continue

            vehicle = self._make_vehicle(box)
            if vehicle is None:
                continue

            vehicles.append(vehicle)

        if len(vehicles) == 1:
            return vehicles[0]

        if len(vehicles) > 1:
            raise ValueError("Multiple vehicles detected in the specified area.")

        return None

    def _make_vehicle(
        self,
        box: detection.Box
    ) -> VehicleObserved | None:
        details=VehicleDetails(
            type=VehicleType(box.type.value),
            color=Color.UNKNOWN
        )
        if details.type == VehicleType.UNKNOWN:
            return None

        vehicle = VehicleObserved(
            details=details,
            coordinate=box.coordinate.to_polygon(),
            score=box.score
        )

        return vehicle

    def _box_in_coordinate(
        self,
        box: detection.Box,
        coordinate: Polygon,
        /
    ) -> bool:
        polygon = self._coordinate_to_np_polygon(coordinate)
        if isinstance(box.coordinate, (BoundingBox, RotatedBoundingBox, Polygon)):
            cx = (box.coordinate.x1 + box.coordinate.x2) / 2
            cy = (box.coordinate.y1 + box.coordinate.y2) / 2
        else:
            raise NotImplementedError("Unsupported box coordinate type.")

        return cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0

    def _coordinate_to_np_polygon(
        self,
        coordinate: Polygon,
        /
    ) -> np.typing.NDArray[np.float32]:
        return np.array(coordinate.to_tuple_list(), dtype=np.int32)
