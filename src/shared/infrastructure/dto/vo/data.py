from typing import Self
from cv2.typing import MatLike

import cv2
import numpy as np

from shared.domain.vo.data import ImageBinary
from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox, Polygon

class Cv2ImageBinary(ImageBinary):
    _encode_extension: str = ".jpeg"
    _encoded_data: bytes | None = None

    def __init__(self, *, image: MatLike) -> None:
        self._image = image

    def data(self) -> bytes:
        if self._encoded_data is None:
            ok, buffer = cv2.imencode(self._encode_extension, self._image)
            if not ok:
                raise RuntimeError("Failed to encode image.")

            self._encoded_data = bytes(buffer.data)

        return self._encoded_data

    def crop(
        self,
        coordinate: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> Self:
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

        return type(self)(
            image=cropped
        )

    def frame(self) -> MatLike:
        return self._image
