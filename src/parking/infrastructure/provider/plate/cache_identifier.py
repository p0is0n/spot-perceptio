from dataclasses import dataclass
from datetime import timedelta

from shared.domain.aggregate.image import Image
from shared.application.tool.image_cache import ImageCache

from shared.domain.vo.coordinate import Polygon
from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

@dataclass(frozen=True, slots=True)
class CachePlateIdentifierResult:
    result: Plate | None


class CachePlateIdentifier(PlateIdentifier):
    _identifier: PlateIdentifier
    _cache: ImageCache[CachePlateIdentifierResult]
    _cache_ttl: timedelta = timedelta(days=1)

    def __init__(
        self,
        identifier: PlateIdentifier,
        cache: ImageCache[CachePlateIdentifierResult],
        /
    ) -> None:
        self._identifier = identifier
        self._cache = cache

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        cached_image = await image.crop(vehicle_coordinate)
        cached = await self._cache.get(cached_image)
        if cached is not None:
            return cached.result

        result = await self._identifier.identify(image, vehicle_coordinate)
        await self._cache.put(
            cached_image,
            CachePlateIdentifierResult(
                result=result
            ),
            ttl=self._cache_ttl
        )

        return result
