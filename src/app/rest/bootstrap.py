from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any
from collections.abc import Callable, AsyncGenerator
from fastapi import FastAPI

from kernel.ui.rest.handler.exception import ExceptionHandler

from di.container import Container
from app.rest.base import create_app

def bootstrap() -> FastAPI:
    container = Container()
    app = create_app(
        lifespan=_make_lifespan(container=container)
    )

    for handler in (ExceptionHandler(), ):
        handler.register(app)

    container.setup(app)

    return app


def _make_lifespan(container: Container) -> Callable[
    [FastAPI], AbstractAsyncContextManager[None]
]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[Any]:
        try:
            yield None
        finally:
            await container.shutdown()

    return lifespan
