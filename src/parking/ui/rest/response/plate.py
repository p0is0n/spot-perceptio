from kernel.ui.rest.base.response import BaseResponse

from parking.ui.rest.response.coordinate import PolygonResponse

class PlateResponse(BaseResponse):
    value: str
    country: str
    coordinate: PolygonResponse
