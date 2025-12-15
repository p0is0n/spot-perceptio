from pathlib import Path
from threading import Lock

import numpy as np
import torch

from cv2.typing import MatLike
from ultralytics import YOLO # type: ignore[attr-defined]
from ultralytics.engine.model import Model
from ultralytics.engine.results import Results

from shared.domain.vo.coordinate import BoundingBox
from shared.domain.aggregate.image import Image

from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.application.service.ml.dto import detection
from shared.application.service.ml.provider.detection import MlDetectionProvider

from shared.infrastructure.dto.vo.data import Cv2ImageBinary

class YOLOMlDetectionProvider(MlDetectionProvider):
    def __init__(
        self,
        worker_pool_factory: WorkerPoolFactory,
        model: Path,
        task: str,
        device: str | None = None,
        /
    ) -> None:
        self._worker_pool = worker_pool_factory.make_with_limits(max_workers=1)
        self._lock = Lock()
        self._model: Model = YOLO(model=model, task=task)

        if device is not None:
            self._model.to(device=device)

    async def predict(self, request: detection.Request, /) -> detection.Response:
        return await self._worker_pool.run(
            self._do_predict,
            request
        )

    def _do_predict(self, request: detection.Request, /) -> detection.Response:
        frame = self._extract_frame(request.source)
        with self._lock:
            with torch.inference_mode():
                results = self._model.predict(
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
            target_cls = set(t.name for t in request.target_types)
            mask &= np.isin(class_ids, list(target_cls))

        idx = np.where(mask)[0]
        if len(idx) == 0:
            return self._make_empty_response()

        response_boxes: list[detection.Box] = []
        for box_idx in idx:
            box = boxes[box_idx]
            xyxy = box.xyxy.cpu().numpy()[0]
            coordinate = self._to_bounding_box_coordinate(xyxy)
            class_id = class_ids[box_idx]
            class_name = results[0].names.get(class_id, "unknown")

            response_boxes.append(detection.Box(
                type=detection.Type(
                    id=class_id,
                    name=class_name
                ),
                score=float(conf_scores[box_idx]),
                coordinate=coordinate
            ))

        return detection.Response(
            id=None,
            boxes=tuple(response_boxes)
        )

    def _to_bounding_box_coordinate(
        self,
        xyxy: np.typing.NDArray[np.float32]
    ) -> BoundingBox:
        return BoundingBox.from_xyxy(
            *map(int, xyxy.tolist())
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
