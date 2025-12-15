from collections.abc import Callable

from shared.infrastructure.service.ml.factory.yolo_provider import YOLOMlDetectionFactory

from parking.domain.provider.vehicle.identifier import VehicleIdentifier
from parking.application import config

from parking.infrastructure.provider.vehicle.yolo_identifier import YOLOVehicleIdentifier

class VehicleIdentifierFactory:
    def __init__(
        self,
        config_ml: config.Ml,
        yolo_ml_detection_factory: YOLOMlDetectionFactory,
        /
    ) -> None:
        self._config_ml = config_ml
        self._yolo_ml_detection_factory = yolo_ml_detection_factory

    def make_all(self) -> tuple[VehicleIdentifier, ...]:
        factories: dict[str, Callable[[], VehicleIdentifier]] = {
            "yolo": self.make_yolo,
        }

        try:
            return tuple(
                factories[identifier]()
                for identifier in self._config_ml.vehicle_identifiers
            )
        except KeyError as exc:
            raise ValueError("Unknown vehicle identifier") from exc

    def make_yolo(self) -> YOLOVehicleIdentifier:
        detection = self._yolo_ml_detection_factory.make(
            self._config_ml.vehicle_identifier_yolo_model_path
        )

        return YOLOVehicleIdentifier(
            self._config_ml,
            detection
        )
