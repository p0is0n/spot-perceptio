from fastapi import APIRouter
from starlette import status

from di.container import Provide, inject

from kernel.application.system.handler import check_health
from kernel.ui.rest.base.response import BaseResponse
from kernel.ui.rest.system.response.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    name="Get Health Status",
    description="Checks the health status of the application."
)
@inject
async def get_health(
    handler: Provide[check_health.Handler]
) -> BaseResponse[HealthResponse]:
    query = check_health.Query()
    result = await handler.handle(query)

    return BaseResponse(
        data=HealthResponse(
            status=result.status,
            time=result.time
        )
    )
