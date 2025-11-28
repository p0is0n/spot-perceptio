from http import HTTPStatus
from typing import Any
from pydantic import Field

from shared.application.dto.base import Base
from shared.application.http.client.dto.base import Data

class Response(Base):
    status: HTTPStatus
    headers: dict[str, str] = Field(default_factory=dict)
    data: Data[Any] | None = None
