from fastapi import APIRouter
from starlette import status

from di.container import Provide, inject

from kernel.application.system.handler import echo
from kernel.ui.rest.base.response import BaseResponse
from kernel.ui.rest.system.response.echo import EchoResponse

router = APIRouter()


@router.get(
    "/echo",
    status_code=status.HTTP_200_OK,
    name="Echo Value",
    description="Echoes the provided value back to the caller."
)
@inject
async def get_echo(
    value: str,
    handler: Provide[echo.Handler]
) -> BaseResponse[EchoResponse]:
    query = echo.Query(value=value)
    result = await handler.handle(query)

    return BaseResponse(
        data=EchoResponse(
            echo=result.echo,
            time=result.time
        )
    )
