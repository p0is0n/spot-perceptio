from dataclasses import dataclass
from typing import Generic, TypeVar
from datetime import timedelta, datetime, UTC
from collections import OrderedDict
from asyncio import Lock

from shared.domain.aggregate.image import Image
from shared.application.tool.image_cache import ImageCache
from shared.application.tool.image_similarity import ImageSimilarity

_T = TypeVar("_T")

@dataclass(frozen=True, slots=True)
class _SimilarityImageCacheEntry(Generic[_T]):
    image: Image
    value: _T
    expires_at: datetime | None


class SimilarityImageCache(Generic[_T], ImageCache[_T]):
    __slots__ = (
        "_max_size",
        "_tolerance",
        "_similarity",
        "_lock",
        "_entries",
    )

    def __init__(
        self,
        *,
        max_size: int,
        tolerance: float,
        similarity: ImageSimilarity,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self._max_size = max_size
        self._tolerance = tolerance
        self._similarity = similarity
        self._lock = Lock()
        self._entries: OrderedDict[
            int,
            _SimilarityImageCacheEntry[_T]
        ] = OrderedDict()

    async def get(self, image: Image, /) -> _T | None:
        now = self._now()
        async with self._lock:
            keys = tuple(self._entries.keys())

        for key in reversed(keys):
            async with self._lock:
                entry = self._entries.get(key)
                if entry is None:
                    continue

                if entry.expires_at is not None and entry.expires_at <= now:
                    del self._entries[key]
                    continue

            is_similar = await self._similarity.similar(
                image,
                entry.image,
                tolerance=self._tolerance
            )
            if is_similar:
                async with self._lock:
                    current = self._entries.get(key)
                    if current is None or not entry is current:
                        continue

                    self._entries.move_to_end(key)
                    return entry.value

        return None

    async def put(
        self,
        image: Image,
        value: _T,
        /,
        ttl: timedelta | None = None
    ) -> None:
        key = self._get_key(image)
        entry = _SimilarityImageCacheEntry(
            image=image,
            value=value,
            expires_at=(
                self._now() + ttl
                if ttl is not None
                else None
            )
        )

        async with self._lock:
            self._entries[key] = entry
            self._entries.move_to_end(key)

            if len(self._entries) > self._max_size:
                self._entries.popitem(last=False)

    def _get_key(self, image: Image, /) -> int:
        return id(image)

    def _now(self) -> datetime:
        return datetime.now(UTC)
