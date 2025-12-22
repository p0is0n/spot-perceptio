from typing import Protocol, TypeVar
from datetime import timedelta

from shared.domain.aggregate.image import Image

_T = TypeVar("_T")

class ImageCache(Protocol[_T]):
    async def get(self, image: Image, /) -> _T | None: ...
    async def put(self, image: Image, value: _T, /, ttl: timedelta | None = None) -> None: ...
