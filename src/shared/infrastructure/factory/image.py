from http import HTTPMethod, HTTPStatus

import cv2
import numpy as np

from cv2.typing import MatLike

from shared.domain.aggregate.image import Image
from shared.domain.vo.coordinate import Coordinate, BoundingBox
from shared.domain.vo.data import ImageBinary
from shared.application.http import client as http_client
from shared.application.factory.image import ImageFactory
from shared.application.dto.contract import income
from shared.infrastructure.dto.vo.data import Cv2ImageBinary

class Cv2ImageFactory(ImageFactory):
    def __init__(self, http: http_client.ClientProtocol) -> None:
        self._http = http

    async def make_from_income(self, image: income.Image, /) -> Image:
        raw_data = await self._extract_raw_bytes(image)
        cv2_data = await self._decode_image(raw_data)

        return self._make_image(cv2_data)

    async def _extract_raw_bytes(self, image: income.Image, /) -> bytes:
        raw_data: bytes | None = None
        if image.data is not None:
            raw_data = image.data
        elif image.url is not None:
            raw_data = await self._extract_raw_bytes_from_url(str(image.url))

        if raw_data is None:
            raise ValueError("Image data is missing, expected either data or url.")

        return raw_data

    async def _extract_raw_bytes_from_url(self, url: str, /) -> bytes:
        try:
            response = await self._http.send(http_client.Request(
                url=url,
                method=HTTPMethod.GET,
                headers={
                    "Accept": "image/*"
                },
                expect_status_codes=(HTTPStatus.OK,)
            ))
        except http_client.UnexpectedStatusError as exc:
            raise ValueError(
                "Failed to fetch image from URL, unexpected status code."
            ) from exc

        if not isinstance(response.data, http_client.BinaryData):
            raise TypeError(
                "Failed to fetch image from URL, invalid response data type.",
                type(response.data)
            )

        return response.data.value

    async def _decode_image(self, data: bytes) -> MatLike:
        cv2_data = cv2.imdecode(
            np.frombuffer(data, dtype=np.uint8),
            cv2.IMREAD_UNCHANGED
        )
        if cv2_data is None:
            raise ValueError("Invalid image data provided, cv2 failed to decode.")

        return cv2_data

    def _make_image(self, cv2_data: MatLike) -> Image:
        data: ImageBinary = Cv2ImageBinary(image=cv2_data)

        h, w = cv2_data.shape[:2]
        coordinate = BoundingBox(
            p1=Coordinate(x=0, y=0),
            p2=Coordinate(x=w, y=h)
        )

        return Image(
            data=data,
            coordinate=coordinate
        )
