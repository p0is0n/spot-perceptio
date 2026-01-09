from shared.domain.vo.coordinate import Polygon
from shared.domain.aggregate.image import Image
from shared.application.log import Logger

from parking.domain.aggregate.vehicle import VehicleObserved
from parking.domain.provider.vehicle.identifier import VehicleIdentifier

class DefaultVehicleIdentifier(VehicleIdentifier):
    def __init__(
        self,
        identifiers: tuple[VehicleIdentifier, ...],
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
            tags=("default_vehicle_identifier", "init"),
        )

    async def identify(
        self,
        image: Image,
        spot_coordinate: Polygon,
        /
    ) -> VehicleObserved | None:
        vehicle_observed: VehicleObserved | None = None
        for identifier in self._identifiers:
            vehicle_observed = await identifier.identify(image, spot_coordinate)
            if vehicle_observed is not None:
                self._logger.debug(
                    "Vehicle identified",
                    data={
                        "image": await image.fingerprint(),
                        "spot_coordinate": spot_coordinate.key(),
                        "vehicle_coordinate": vehicle_observed.coordinate.key(),
                        "identifier": identifier.__class__.__name__,
                    },
                    tags=("default_vehicle_identifier", "identify"),
                )

                return vehicle_observed

        self._logger.debug(
            "Vehicle not identified",
            data={
                "image": await image.fingerprint(),
                "spot_coordinate": spot_coordinate.key(),
            },
            tags=("default_vehicle_identifier", "identify"),
        )

        return None
