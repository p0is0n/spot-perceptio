from fastapi import APIRouter

from parking.ui.rest.action.analyze_spot import router as analyze_spot_router

parking_router = APIRouter(
    prefix="/parking",
    tags=["parking"]
)

parking_router.include_router(analyze_spot_router)
