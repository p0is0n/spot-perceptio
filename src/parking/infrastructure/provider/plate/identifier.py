from shared.domain.aggregate.image import Image
from shared.domain.vo.coordinate import Polygon
from shared.application.log import Logger

from parking.domain.vo.plate import Plate
from parking.domain.provider.plate.identifier import PlateIdentifier

class DefaultPlateIdentifier(PlateIdentifier):
    def __init__(
        self,
        identifiers: tuple[PlateIdentifier, ...],
        logger: Logger,
        /
    ) -> None:
        self._identifiers = identifiers
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={
                "identifiers": len(self._identifiers),
            },
            tags=("default_plate_identifier", "init"),
        )

    async def identify(
        self,
        image: Image,
        vehicle_coordinate: Polygon,
        /
    ) -> Plate | None:
        plate: Plate | None = None
        for identifier in self._identifiers:
            plate = await identifier.identify(image, vehicle_coordinate)
            if plate is not None:
                self._logger.debug(
                    "Plate identified",
                    data={
                        "image": await image.fingerprint(),
                        "vehicle_coordinate": vehicle_coordinate.key(),
                        "plate_coordinate": plate.coordinate.key(),
                        "identifier": identifier.__class__.__name__,
                    },
                    tags=("default_plate_identifier", "identify"),
                )

                return plate

        self._logger.debug(
            "Plate not identified",
            data={
                "image": await image.fingerprint(),
                "vehicle_coordinate": vehicle_coordinate.key(),
            },
            tags=("default_plate_identifier", "identify"),
        )

        return None
