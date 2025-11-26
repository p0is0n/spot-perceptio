from typing import Annotated
from fastapi import APIRouter, Query, status

from di.container import Provide, inject

from kernel.application.system.handler import echo
from kernel.ui.rest.base.response import Response
from kernel.ui.rest.system.request.echo import EchoRequest
from kernel.ui.rest.system.response.echo import EchoResponse

router = APIRouter()

@router.get(
    "/echo",
    status_code=status.HTTP_200_OK,
    name="Test system with echo value",
    description="Returns the echoed value along."
)
@inject
async def get_echo(
    request: Annotated[EchoRequest, Query()],
    handler: Provide[echo.Handler]
) -> Response[EchoResponse]:
    command = echo.Command(value=request.value)
    result = await handler.handle(command)

    return Response[EchoResponse](
        data=EchoResponse(
            echo=result.echo,
            time=result.time
        )
    )
