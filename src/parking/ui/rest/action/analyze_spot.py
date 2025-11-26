from typing import Annotated
from fastapi import APIRouter, Body, status

from di.container import Provide, inject
from kernel.ui.rest.base.response import Response

from parking.application.handler import analyze_spot
from parking.ui.rest.request.analyze_spot import AnalyzeSpotRequest
from parking.ui.rest.response.analyze_spot import AnalyzeSpotResponse
from parking.ui.rest.mapper.request_command import RequestCommandMapper
from parking.ui.rest.mapper.contract_response import ContractResponseMapper

router = APIRouter()

@router.put(
    "/analyze_spot",
    status_code=status.HTTP_200_OK,
    name="Analyze parking spot",
    description="Returns analysis of a parking spot based on the provided data.",
)
@inject
async def put_analyze_spot(
    request: Annotated[AnalyzeSpotRequest, Body()],
    request_mapper: Provide[RequestCommandMapper],
    response_mapper: Provide[ContractResponseMapper],
    handler: Provide[analyze_spot.Handler]
) -> Response[AnalyzeSpotResponse]:
    command = request_mapper.make_analyze_spot(request)
    result = await handler.handle(command)

    return Response[AnalyzeSpotResponse](
        data=response_mapper.make_analyze_spot(result)
    )
