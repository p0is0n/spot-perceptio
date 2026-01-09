from dataclasses import dataclass
from datetime import timedelta

from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image

from shared.application.log import Logger
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
        logger: Logger,
        /
    ) -> None:
        self._identifier = identifier
        self._cache = cache
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={},
            tags=("cache_vehicle_identifier", "init"),
        )

    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        self._logger.debug(
            "Identify cache",
            data={
                "image": await image.fingerprint(),
                "spot_coordinate": spot_coordinate.key(),
            },
            tags=("cache_vehicle_identifier", "identify"),
        )

        cached_image = await image.crop(spot_coordinate)
        cached = await self._cache.get(cached_image)
        if cached is not None:
            self._logger.debug(
                "Identify cache hit",
                data={
                    "image": await image.fingerprint(),
                    "spot_coordinate": spot_coordinate.key(),
                    "vehicle_coordinate": (cached.result.coordinate.key()
                                           if cached.result is not None else None),
                },
                tags=("cache_vehicle_identifier", "identify"),
            )

            return cached.result

        result = await self._identifier.identify(image, spot_coordinate)
        await self._cache.put(
            cached_image,
            CacheVehicleIdentifierResult(
                result=result
            ),
            ttl=self._cache_ttl
        )

        self._logger.debug(
            "Identify cache miss",
            data={
                "image": await image.fingerprint(),
                "spot_coordinate": spot_coordinate.key(),
            },
            tags=("cache_vehicle_identifier", "identify"),
        )

        return result
