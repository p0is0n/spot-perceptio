import cv2
import numpy as np

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image
from shared.application.service.ml.provider.detection import MlDetectionProvider
from shared.application.service.ml.dto import detection

from parking.domain.aggregate.vehicle import VehicleDetails, VehicleObserved
from parking.domain.enum.color import Color
from parking.domain.enum.vehicle import VehicleType
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class YOLOVehicleIdentifier(VehicleIdentifier):
    _imgsz: int = 640
    _threshold: float
    _threshold_overlap: float = 0.3
    _expand_margin: int = 40

    _vehicles_types: dict[str, VehicleType] = {
        "bicycle": VehicleType.BICYCLE,
        "motorcycle": VehicleType.MOTORCYCLE,
        "car": VehicleType.CAR,
        "bus": VehicleType.BUS,
        "truck": VehicleType.TRUCK
    }

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
        result = await self._process_response(image, spot_coordinate, response)

        return result

    async def _process_response(
        self,
        image: Image,
        coordinate: Polygon,
        response: detection.Response,
        /
    ) -> VehicleObserved | None:
        if len(response.boxes) == 0:
            return None

        best_vehicle: VehicleObserved | None = None
        best_score: float = 0.0
        for box in response.boxes:
            if box.score < self._threshold:
                continue

            overlap = self._box_overlap_ratio(box, coordinate)
            if overlap < self._threshold_overlap:
                continue

            vehicle = self._make_vehicle(image, box)
            if vehicle is None:
                continue

            final_score = overlap * box.score
            if final_score > best_score:
                best_score = final_score
                best_vehicle = vehicle

        return best_vehicle

    def _make_vehicle(
        self,
        image: Image,
        box: detection.Box,
        /
    ) -> VehicleObserved | None:
        details=VehicleDetails(
            type=self._vehicles_types.get(box.type.name, VehicleType.UNKNOWN),
            color=Color.UNKNOWN
        )
        if details.type == VehicleType.UNKNOWN:
            return None

        polygon = box.coordinate.to_polygon().expand(self._expand_margin, image.coordinate)
        vehicle = VehicleObserved(
            details=details,
            coordinate=polygon,
            score=box.score
        )

        return vehicle

    def _box_overlap_ratio(
        self,
        box: detection.Box,
        coordinate: Polygon,
        /
    ) -> float:
        spot = self._coordinate_to_np_polygon(coordinate)
        vehicle = self._coordinate_to_np_polygon(box.coordinate.to_polygon())

        vehicle_area = cv2.contourArea(vehicle)
        if vehicle_area <= 0:
            return 0.0

        intersection_area, _ = cv2.intersectConvexConvex(spot, vehicle)
        if intersection_area <= 0:
            return 0.0

        return intersection_area / vehicle_area

    def _coordinate_to_np_polygon(
        self,
        coordinate: Polygon,
        /
    ) -> np.typing.NDArray[np.float32]:
        return np.array(coordinate.to_tuple_list(), dtype=np.float32)
