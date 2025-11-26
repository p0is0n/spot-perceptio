import numpy as np
import torch

from cv2.typing import MatLike
from ultralytics import YOLO # type: ignore[attr-defined]
from ultralytics.engine.model import Model
from ultralytics.engine.results import Results

from shared.domain.vo.coordinate import Coordinate, BoundingBox
from shared.domain.aggregate.image import Image
from shared.application.service.ml.dto import detection
from shared.application.service.ml.provider.detection import MLDetectionProvider
from shared.infrastructure.dto.vo.data import Cv2ImageBinary

class YOLOMLDetectionProvider(MLDetectionProvider):
    _source_imgsz: int = 640
    _score_threshold: float = 0.70
    _vehicles_types: dict[int, detection.Type] = {
        1: detection.Type.BICYCLE,
        3: detection.Type.MOTORCYCLE,
        2: detection.Type.CAR,
        5: detection.Type.BUS,
        7: detection.Type.TRUCK,
    }

    def __init__(self, model: str, /, task: str = "detect") -> None:
        self._model: Model = YOLO(
            model=model,
            task=task,
            verbose=False
        )
        self._model.to("cpu")

    async def predict(self, request: detection.Request, /) -> detection.Response:
        frame = self._extract_frame(request.source)
        results = self._model(
            source=frame
        )

        return self._process_results(request, results)

    def _extract_frame(self, image: Image, /) -> MatLike:
        if isinstance(image.data, Cv2ImageBinary):
            return image.data.frame()

        raise TypeError("Unsupported image data type for frame extraction.")

    def _process_results(
        self,
        request: detection.Request,
        results: list[Results],
        /
    ) -> detection.Response:
        if len(results) == 0:
            return self._make_empty_response()

        if len(results) != 1:
            raise ValueError("Expected exactly one result from the model.")

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return self._make_empty_response()

        conf_scores = self._detach_as(boxes.conf)
        class_ids = self._detach_as(boxes.cls).astype(int)

        mask = np.ones_like(conf_scores, dtype=bool)
        if request.score_threshold is not None:
            mask &= (conf_scores >= request.score_threshold)

        if request.target_types is not None:
            target_cls = set(t.value for t in request.target_types)
            mask &= np.isin(class_ids, list(target_cls))

        idx = np.where(mask)[0]
        if len(idx) == 0:
            return self._make_empty_response()

        response_boxes: list[detection.Box] = []
        for box_idx in idx:
            box = boxes[box_idx]
            xyxy = box.xyxy.cpu().numpy()[0]
            coordinate = self._to_bounding_box_coordinate(xyxy)

            response_boxes.append(detection.Box(
                type=self._to_detection_type(class_ids[box_idx]),
                score=float(conf_scores[box_idx]),
                coordinate=coordinate
            ))

        return detection.Response(
            id=None,
            boxes=tuple(response_boxes)
        )

    def _to_detection_type(self, class_id: int) -> detection.Type:
        return self._vehicles_types.get(
            class_id,
            detection.Type.UNKNOWN
        )

    def _to_bounding_box_coordinate(
        self,
        xyxy: np.typing.NDArray[np.float32]
    ) -> BoundingBox:
        x1, y1, x2, y2 = map(int, xyxy.tolist())

        return BoundingBox(
            p1=Coordinate(x=x1, y=y1),
            p2=Coordinate(x=x2, y=y2),
        )

    def _detach_as(
        self,
        x: torch.Tensor | np.typing.NDArray[np.float32]
    ) -> np.typing.NDArray[np.float32]:
        if isinstance(x, torch.Tensor):
            return x.detach().cpu().numpy()

        return x

    def _make_empty_response(self) -> detection.Response:
        return detection.Response(
            id=None,
            boxes=()
        )
