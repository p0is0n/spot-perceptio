from typing import Any
from collections.abc import Sequence
from pydantic import ValidationError as PydanticValidationError

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder

from kernel.ui.rest.handler.base import Handler

class ExceptionHandler(Handler):
    def register(self, app: FastAPI, /) -> None:
        app.add_exception_handler(RequestValidationError, self.on_validation_error)
        app.add_exception_handler(PydanticValidationError, self.on_pydantic_validation_error)
        app.add_exception_handler(Exception, self.on_unexpected_error)

    async def on_validation_error(
        self,
        request: Request,
        exc: Exception
    ) -> Response:
        if not isinstance(exc, RequestValidationError):
            return await self.on_unexpected_error(request, exc)

        return self._make_json_response_error(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            errors=exc.errors()
        )

    async def on_pydantic_validation_error(
        self,
        request: Request,
        exc: Exception
    ) -> Response:
        if not isinstance(exc, PydanticValidationError):
            return await self.on_unexpected_error(request, exc)

        return self._make_json_response_error(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            errors=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False
            )
        )

    async def on_unexpected_error(
        self,
        request: Request,
        exc: Exception
    ) -> Response:
        return self._make_json_response_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[{
                "loc": [],
                "type": "unexpected_error",
                "msg": "Unexpected system error"
            }]
        )

    def _make_json_response_error(self,
        *,
        status_code: int,
        errors: Sequence[Any]
    ) -> Response:
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": jsonable_encoder(errors),
            }
        )
