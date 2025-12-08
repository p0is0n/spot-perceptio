from pydantic import NonNegativeInt

from kernel.ui.rest.base.response import BaseResponse

class CoordinateResponse(BaseResponse):
    x: NonNegativeInt
    y: NonNegativeInt


class BoundingBoxResponse(BaseResponse):
    p1: CoordinateResponse
    p2: CoordinateResponse


class PolygonResponse(BaseResponse):
    corners: tuple[CoordinateResponse, ...]
