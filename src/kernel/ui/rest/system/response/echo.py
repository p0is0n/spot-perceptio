from datetime import datetime
from pydantic import BaseModel

class EchoResponse(BaseModel):
    echo: str
    time: datetime
