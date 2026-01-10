from kernel.ui.rest.base.response import BaseResponse

from parking.ui.rest.response.spot import ParkingSpotResponse

class AnalyzeSpotsResponse(BaseResponse):
    parking_spots: tuple[ParkingSpotResponse, ...]
