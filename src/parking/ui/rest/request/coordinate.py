from pydantic import NonNegativeInt

from kernel.ui.rest.base.request import BaseRequest

class CoordinateRequest(BaseRequest):
    x: NonNegativeInt
    y: NonNegativeInt


class BoundingBoxRequest(BaseRequest):
    p1: CoordinateRequest
    p2: CoordinateRequest


class PolygonRequest(BaseRequest):
    corners: tuple[CoordinateRequest, ...]
