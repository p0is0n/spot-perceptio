from http.client import HTTPException
from http import HTTPStatus

class ClientError(HTTPException):
    pass

class ResponseError(ClientError):
    status: HTTPStatus | None = None

    def __init__(self, status: HTTPStatus, message: str) -> None:
        self.status = status
        super().__init__(message)


class UnexpectedStatusError(ResponseError):
    def __init__(
        self,
        status: HTTPStatus,
        message: str = "Unexpected HTTP status in response"
    ) -> None:
        super().__init__(status, message)


class DecodeBodyError(ResponseError):
    def __init__(
        self,
        status: HTTPStatus,
        message: str = "Failed to decode response body"
    ) -> None:
        super().__init__(status, message)
