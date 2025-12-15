from cv2.typing import MatLike
import hyperlpr3 as lpr3 # type: ignore

from shared.domain.aggregate.image import Image
from shared.domain.vo.coordinate import Polygon, BoundingBox
from shared.domain.enum.country import Country

from shared.application.tool.worker_pool import WorkerPool
from shared.infrastructure.dto.vo.data import Cv2ImageBinary

from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

from parking.application import config

class HyperlprPlateIdentifier(PlateIdentifier):
    _imgsz: int = 640
    _expand_margin: int = 20

    def __init__(
        self,
        config_ml: config.Ml,
        worker_pool: WorkerPool
    ) -> None:
        self._threshold = config_ml.plate_identifier_hyperlpr_threshold
        self._worker_pool = worker_pool
        self._catcher = lpr3.LicensePlateCatcher(
            detect_level=lpr3.DETECT_LEVEL_HIGH
        )

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        vehicle_image = await image.crop(vehicle_coordinate)

        return await self._worker_pool.run(
            self._do_identify,
            vehicle_image,
            vehicle_coordinate
        )

    def _do_identify(
        self,
        vehicle_image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        frame = self._extract_frame(vehicle_image)
        frame = self._prepare_image(frame)

        response = self._catcher(frame)

        return self._process_response(
            response,
            vehicle_coordinate
        )

    def _process_response(
        self,
        response: list[tuple[
            str, float, int, tuple[
                int,
                int,
                int,
                int
            ]
        ]],
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        if not response:
            return None

        best = max(response, key=lambda x: float(x[1]))
        score = best[1]

        if score < self._threshold:
            return None

        plate_text = best[0]
        x1, y1, x2, y2 = best[3]

        offset_x = vehicle_coordinate.x1
        offset_y = vehicle_coordinate.y1

        global_poly = BoundingBox.from_xyxy(
            x1 + offset_x,
            y1 + offset_y,
            x2 + offset_x,
            y2 + offset_y
        ).to_polygon().expand(self._expand_margin, vehicle_coordinate)

        return Plate(
            value=plate_text,
            country=Country.UNKNOWN,
            coordinate=global_poly
        )

    def _prepare_image(self, frame: MatLike, /) -> MatLike:
        return frame

    def _extract_frame(self, image: Image, /) -> MatLike:
        if isinstance(image.data, Cv2ImageBinary):
            return image.data.frame()

        raise TypeError("Unsupported image data type for frame extraction.")
