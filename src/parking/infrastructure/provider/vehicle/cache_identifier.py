from dataclasses import dataclass
from datetime import timedelta

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image
from shared.application.tool.image_cache import ImageCache

from parking.domain.aggregate.vehicle import VehicleObserved
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

@dataclass(frozen=True, slots=True)
class CacheVehicleIdentifierResult:
    result: VehicleObserved | None


class CacheVehicleIdentifier(VehicleIdentifier):
    _identifier: VehicleIdentifier
    _cache: ImageCache[CacheVehicleIdentifierResult]
    _cache_ttl: timedelta = timedelta(days=1)

    def __init__(
        self,
        identifier: VehicleIdentifier,
        cache: ImageCache[CacheVehicleIdentifierResult],
        /
    ) -> None:
        self._identifier = identifier
        self._cache = cache

    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        cached_image = await image.crop(spot_coordinate)
        cached = await self._cache.get(cached_image)
        if cached is not None:
            return cached.result

        result = await self._identifier.identify(image, spot_coordinate)
        await self._cache.put(
            cached_image,
            CacheVehicleIdentifierResult(
                result=result
            ),
            ttl=self._cache_ttl
        )

        return result
