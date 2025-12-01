from kernel.ui.rest.base.response import BaseResponse

from parking.ui.rest.response.plate import PlateResponse

class VehicleDetailsResponse(BaseResponse):
    type: str
    color: str


class VehicleResponse(BaseResponse):
    details: VehicleDetailsResponse
    plate: PlateResponse | None
