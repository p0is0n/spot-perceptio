from typing import Annotated
from fastapi import APIRouter, Body, status

from di.container import Provide, inject
from kernel.ui.rest.base.response import Response

from parking.application.handler import analyze_spots
from parking.ui.rest.request.analyze_spots import AnalyzeSpotsRequest
from parking.ui.rest.response.analyze_spots import AnalyzeSpotsResponse
from parking.ui.rest.mapper.request_command import RequestCommandMapper
from parking.ui.rest.mapper.contract_response import ContractResponseMapper

router = APIRouter()

@router.put(
    "/analyze_spots",
    status_code=status.HTTP_200_OK,
    name="Analyze multiple parking spots from one image",
    description="Returns analysis of a parking spots based on the provided data.",
)
@inject
async def put_analyze_spot(
    request: Annotated[AnalyzeSpotsRequest, Body()],
    request_mapper: Provide[RequestCommandMapper],
    response_mapper: Provide[ContractResponseMapper],
    handler: Provide[analyze_spots.Handler]
) -> Response[AnalyzeSpotsResponse]:
    command = request_mapper.make_analyze_spots(request)
    result = await handler.handle(command)

    return Response[AnalyzeSpotsResponse](
        data=response_mapper.make_analyze_spots(result)
    )
