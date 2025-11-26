from kernel.ui.rest.base.response import BaseResponse

from parking.ui.rest.response.spot import ParkingSpotResponse

class AnalyzeSpotResponse(BaseResponse):
    parking_spot: ParkingSpotResponse
