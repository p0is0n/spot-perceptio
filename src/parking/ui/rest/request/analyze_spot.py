from kernel.ui.rest.base.request import BaseRequest

from parking.ui.rest.request.image import ImageRequest
from parking.ui.rest.request.spot import SpotRequest

class AnalyzeSpotRequest(BaseRequest):
    image: ImageRequest
    spot: SpotRequest
