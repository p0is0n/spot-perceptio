from pydantic import Base64Bytes, HttpUrl

from kernel.ui.rest.base.request import BaseRequest

class ImageRequest(BaseRequest):
    data: Base64Bytes | None = None
    url: HttpUrl | None = None
