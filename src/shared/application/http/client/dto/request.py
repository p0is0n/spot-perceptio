from http import HTTPMethod, HTTPStatus
from typing import Any
from pydantic import HttpUrl, PositiveFloat, Field

from shared.application.dto.base import Base
from shared.application.http.client.dto.base import Data

class Request(Base):
    url: HttpUrl
    method: HTTPMethod
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, str | int | float] | None = None
    payload: Data[Any] | None = None
    timeout: PositiveFloat | None = None
    expect_status_codes: tuple[HTTPStatus, ...] | None = None
