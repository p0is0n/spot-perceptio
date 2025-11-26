from kernel.ui.rest.base.response import BaseResponse

from parking.ui.rest.response.vehicle import VehicleResponse

class SpotResponse(BaseResponse):
    id: str


class ParkingSpotResponse(BaseResponse):
    occupied: bool
    spot: SpotResponse
    vehicle: VehicleResponse | None = None
