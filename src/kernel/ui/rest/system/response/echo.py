from datetime import datetime
from pydantic import Field

from kernel.ui.rest.base.response import BaseResponse

class EchoResponse(BaseResponse):
    echo: str
    time: datetime = Field(strict=True)
