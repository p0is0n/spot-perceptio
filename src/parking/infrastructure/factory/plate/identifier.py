from collections.abc import Callable

from shared.application.tool.worker_pool import WorkerPool
from shared.infrastructure.service.ml.factory.yolo_provider import YOLOMlDetectionFactory

from parking.domain.provider.plate.identifier import PlateIdentifier
from parking.application import config

from parking.infrastructure.provider.plate.hyperlpr_identifier import HyperlprPlateIdentifier
from parking.infrastructure.provider.plate.yolo_identifier import YOLOPlateIdentifier

class PlateIdentifierFactory:
    def __init__(
        self,
        config_ml: config.Ml,
        yolo_ml_detection_factory: YOLOMlDetectionFactory,
        worker_pool: WorkerPool,
        /
    ) -> None:
        self._config_ml = config_ml
        self._yolo_ml_detection_factory = yolo_ml_detection_factory
        self._worker_pool = worker_pool

    def make_all(self) -> tuple[PlateIdentifier, ...]:
        factories: dict[str, Callable[[], PlateIdentifier]] = {
            "hyperlpr": self.make_hyperlpr,
            "yolo": self.make_yolo,
        }

        try:
            return tuple(
                factories[identifier]()
                for identifier in self._config_ml.plate_identifiers
            )
        except KeyError as exc:
            raise ValueError("Unknown plate identifier") from exc

    def make_hyperlpr(self) -> HyperlprPlateIdentifier:
        return HyperlprPlateIdentifier(
            self._config_ml,
            self._worker_pool
        )

    def make_yolo(self) -> YOLOPlateIdentifier:
        detection = self._yolo_ml_detection_factory.make(
            self._config_ml.plate_identifier_yolo_model_path
        )

        return YOLOPlateIdentifier(
            self._config_ml,
            detection
        )
