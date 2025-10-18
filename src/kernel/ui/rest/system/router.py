from fastapi import APIRouter

from kernel.ui.rest.system.action.health import router as health_router
from kernel.ui.rest.system.action.echo import router as echo_router

system_router = APIRouter(
    prefix="/system",
    tags=["system"]
)

system_router.include_router(health_router)
system_router.include_router(echo_router)
