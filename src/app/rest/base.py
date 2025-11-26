from contextlib import AbstractAsyncContextManager
from collections.abc import Callable
from fastapi import FastAPI

from kernel.ui.rest.system.router import system_router
from parking.ui.rest.router import parking_router

def create_app(
    lifespan: Callable[[FastAPI], AbstractAsyncContextManager[None]]
) -> FastAPI:
    app = FastAPI(
        title="Spot Perceptio API",
        description="API for Spot Perceptio application",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/docs/openapi.json",
        redoc_url=None,
        redirect_slashes=False,
        lifespan=lifespan,
    )

    app.include_router(system_router)
    app.include_router(parking_router)

    return app
