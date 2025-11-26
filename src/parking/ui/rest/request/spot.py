from kernel.ui.rest.base.request import BaseRequest

from parking.ui.rest.request.coordinate import PolygonRequest

class SpotRequest(BaseRequest):
    id: str
    coordinate: PolygonRequest
