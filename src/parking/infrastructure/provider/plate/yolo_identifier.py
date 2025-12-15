from shared.domain.aggregate.image import Image
from shared.domain.vo.coordinate import Polygon
from shared.domain.enum.country import Country

from shared.application.service.ml.provider.detection import MlDetectionProvider
from shared.application.service.ml.dto import detection

from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

from parking.application import config

class YOLOPlateIdentifier(PlateIdentifier):
    _imgsz: int = 640
    _expand_margin: int = 20

    _types: tuple[str, ...] = (
        "license_plate",
    )

    def __init__(
        self,
        config_ml: config.Ml,
        provider: MlDetectionProvider,
        /
    ) -> None:
        self._threshold = config_ml.plate_identifier_yolo_threshold
        self._provider = provider

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        vehicle_image = await image.crop(vehicle_coordinate)
        response = await self._provider.predict(detection.Request(
            source=vehicle_image,
            image_size=self._imgsz
        ))
        result = await self._process_response(vehicle_coordinate, response)

        return result

    async def _process_response(
        self,
        vehicle_coordinate: Polygon,
        response: detection.Response,
        /
    ) -> Plate | None:
        if len(response.boxes) == 0:
            return None

        best_plate: Plate | None = None
        best_score: float = 0.0
        for box in response.boxes:
            if box.score < self._threshold:
                continue

            plate = await self._identify_license_plate(vehicle_coordinate, box)
            if plate is None:
                continue

            if box.score > best_score:
                best_score = box.score
                best_plate = plate

        return best_plate

    async def _identify_license_plate(
        self,
        vehicle_coordinate: Polygon,
        box: detection.Box,
        /
    ) -> Plate | None:
        if not box.type.name in self._types:
            return None

        local_polygon = box.coordinate.to_polygon()
        global_polygon = local_polygon \
            .shift_by(vehicle_coordinate) \
            .expand(self._expand_margin, vehicle_coordinate)

        return Plate(
            value="UNKNOWN",
            country=Country.UNKNOWN,
            coordinate=global_polygon
        )
