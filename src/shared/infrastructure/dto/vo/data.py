import asyncio

from typing import Self
from hashlib import md5

from cv2.typing import MatLike

import cv2
import numpy as np

from shared.domain.vo.data import ImageBinary
from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox, Polygon

from shared.application.tool.worker_pool import WorkerPool

class Cv2ImageBinary(ImageBinary):
    _encode_extension: str = ".jpeg"
    _encoded_data: bytes | None = None
    _image_hash: str | None = None

    def __init__(
        self,
        *,
        image: MatLike,
        worker_pool: WorkerPool
    ) -> None:
        self._image = image
        self._worker_pool = worker_pool
        self._lock = asyncio.Lock()

    async def data(self) -> bytes:
        if self._encoded_data is not None:
            return self._encoded_data

        async with self._lock:
            if self._encoded_data is None:
                ok, buffer = await self._worker_pool.run(
                    cv2.imencode,
                    self._encode_extension,
                    self._image
                )
                if not ok:
                    raise RuntimeError("Failed to encode image.")

                self._encoded_data = bytes(buffer.data)

        return self._encoded_data

    async def hash(self) -> str:
        if self._image_hash is not None:
            return self._image_hash

        bytes_data = await self.data()
        async with self._lock:
            if self._image_hash is None:
                bytes_hash = await self._worker_pool.run(
                    self._get_hash,
                    bytes_data
                )

                self._image_hash = bytes_hash

        return self._image_hash

    async def crop(
        self,
        coordinate: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> Self:
        cropped = await self._worker_pool.run(
            self._crop_image,
            coordinate
        )

        return type(self)(
            image=cropped,
            worker_pool=self._worker_pool
        )

    def frame(self) -> MatLike:
        return self._image

    def _crop_image(
        self,
        coordinate: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> MatLike:
        cropped: MatLike | None = None

        if isinstance(coordinate, Polygon):
            mask = np.zeros(self._image.shape[:2], dtype=np.uint8)
            pts = np.array(coordinate.to_tuple_list(), dtype=np.int32)

            cv2.fillPoly(mask, [pts], (255,))

            masked = cv2.bitwise_and(self._image, self._image, mask=mask)
            x, y, w, h = cv2.boundingRect(pts)

            cropped = masked[y:y+h, x:x+w].copy()
        else:
            raise NotImplementedError("Cropping for selected coordinates is not supported.")

        if cropped is None:
            raise ValueError("Cropping image failed.")

        return cropped

    def _get_hash(self, value: bytes) -> str:
        return md5(value).hexdigest()
