from fastapi import FastAPI
from kernel.ui.rest.system.router import system_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Spot Perceptio API",
        openapi_url="/openapi.json",
        redirect_slashes=False,
    )

    app.include_router(system_router)

    return app
