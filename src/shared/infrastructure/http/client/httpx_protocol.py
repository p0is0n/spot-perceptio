from http import HTTPStatus
from typing import Any

import json
import httpx

from shared.application.http import client as http_client

class HttpxClientProtocol(http_client.ClientProtocol):
    async def send(self, request: http_client.Request, /) -> http_client.Response:
        try:
            async with self._make_client() as client:
                response = await client.request(
                    method=request.method.value,
                    url=str(request.url),
                    headers=request.headers,
                    params=request.params,
                    content=self._encode_payload(request.payload),
                    timeout=request.timeout,
                )
        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
            httpx.HTTPError
        ) as exc:
            raise http_client.ClientError(str(exc)) from exc

        return self._process_response(request, response)

    def _encode_payload(
        self,
        payload: http_client.Data[Any] | None,
        /
    ) -> bytes | str | None:
        if payload is None:
            return None

        if isinstance(payload, http_client.TextData):
            return payload.value

        if isinstance(payload, http_client.JsonData):
            return json.dumps(payload.value)

        if isinstance(payload, http_client.BinaryData):
            return payload.value

        raise http_client.ClientError("Unsupported payload type")

    def _process_response(
        self,
        request: http_client.Request,
        httpx_response: httpx.Response,
        /
    ) -> http_client.Response:
        status = HTTPStatus(httpx_response.status_code)
        headers = dict(httpx_response.headers)

        if request.expect_status_codes is not None:
            if status not in request.expect_status_codes:
                raise http_client.UnexpectedStatusError(
                    status=status
                )

        return http_client.Response(
            status=status,
            headers=headers,
            data=self._process_response_body(httpx_response)
        )

    def _process_response_body(
        self,
        httpx_response: httpx.Response,
        /
    ) -> http_client.Data[Any] | None:
        content_type = httpx_response.headers.get("content-type", "")
        if not isinstance(content_type, str):
            content_type = str(content_type)

        if content_type.startswith("text/"):
            return http_client.TextData(httpx_response.text)

        if content_type.startswith("application/json"):
            try:
                return http_client.JsonData(
                    httpx_response.json()
                )
            except json.JSONDecodeError as exc:
                raise http_client.DecodeBodyError(
                    status=HTTPStatus(httpx_response.status_code)
                ) from exc

        return http_client.BinaryData(value=httpx_response.content)

    def _make_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient()
