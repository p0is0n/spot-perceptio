from kernel.ui.rest.base.response import BaseResponse

class VehicleDetailsResponse(BaseResponse):
    type: str
    color: str


class VehicleResponse(BaseResponse):
    details: VehicleDetailsResponse
