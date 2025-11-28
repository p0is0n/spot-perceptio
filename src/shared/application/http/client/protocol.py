from typing import Protocol

from shared.application.http.client.dto.request import Request
from shared.application.http.client.dto.response import Response

class ClientProtocol(Protocol):
    async def send(self, request: Request, /) -> Response: ...
