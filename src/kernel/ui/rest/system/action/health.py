from fastapi import APIRouter, status

from di.container import Provide, inject

from kernel.application.system.handler import check_health
from kernel.ui.rest.base.response import Response
from kernel.ui.rest.system.response.health import HealthResponse

router = APIRouter()

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    name="Get system health status",
    description="Checks the health status of the application."
)
@inject
async def get_health(
    handler: Provide[check_health.Handler]
) -> Response[HealthResponse]:
    query = check_health.Query()
    result = await handler.handle(query)

    return Response[HealthResponse](
        data=HealthResponse(
            status=result.status,
            time=result.time
        )
    )
