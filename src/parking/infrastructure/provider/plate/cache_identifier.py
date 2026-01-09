from dataclasses import dataclass
from datetime import timedelta

from shared.domain.aggregate.image import Image
from shared.application.tool.image_cache import ImageCache
from shared.application.log import Logger

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
        logger: Logger,
        /
    ) -> None:
        self._identifier = identifier
        self._cache = cache
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={},
            tags=("cache_plate_identifier", "init"),
        )

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        self._logger.debug(
            "Identify cache",
            data={
                "image": await image.fingerprint(),
                "vehicle_coordinate": vehicle_coordinate.key(),
            },
            tags=("cache_plate_identifier", "identify"),
        )

        cached_image = await image.crop(vehicle_coordinate)
        cached = await self._cache.get(cached_image)
        if cached is not None:
            self._logger.debug(
                "Identify cache hit",
                data={
                    "image": await image.fingerprint(),
                    "vehicle_coordinate": vehicle_coordinate.key(),
                    "plate_coordinate": (cached.result.coordinate.key()
                                         if cached.result is not None else None),
                },
                tags=("cache_plate_identifier", "identify"),
            )

            return cached.result

        result = await self._identifier.identify(image, vehicle_coordinate)
        await self._cache.put(
            cached_image,
            CachePlateIdentifierResult(
                result=result
            ),
            ttl=self._cache_ttl
        )

        self._logger.debug(
            "Identify cache miss",
            data={
                "image": await image.fingerprint(),
                "vehicle_coordinate": vehicle_coordinate.key(),
            },
            tags=("cache_plate_identifier", "identify"),
        )

        return result
