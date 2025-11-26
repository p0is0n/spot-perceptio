from datetime import datetime
from pydantic import Field

from kernel.ui.rest.base.response import BaseResponse

class HealthResponse(BaseResponse):
    status: str
    time: datetime = Field(strict=True)
