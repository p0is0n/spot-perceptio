from dishka import provide, provide_all

from di.container.dishka.providers.provider import Provider

from shared.application import config as shared_config
from shared.application.service.ml.provider.detection import MlDetectionProvider
from shared.infrastructure.service.ml.provider.yolo_provider import YOLOMlDetectionProvider

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.service.vehicle.recognizer import VehicleRecognizer
from parking.domain.provider.vehicle.identifier import VehicleIdentifier
from parking.domain.provider.plate.identifier import PlateIdentifier

from parking.application import config
from parking.application.factory.contract import ContractFactory
from parking.application.factory.contract_income import ContractIncomeFactory
from parking.application.handler import analyze_spot

from parking.infrastructure.provider.vehicle.identifier import DefaultVehicleIdentifier
from parking.infrastructure.provider.vehicle.ml_detection_identifier import (
    MlDetectionVehicleIdentifier
)
from parking.infrastructure.provider.plate.identifier import DefaultPlateIdentifier
from parking.infrastructure.provider.plate.ml_detection_identifier import (
    MlDetectionPlateIdentifier
)

from parking.ui.rest.mapper.request_income import RequestIncomeMapper
from parking.ui.rest.mapper.contract_response import ContractResponseMapper
from parking.ui.rest.mapper.request_command import RequestCommandMapper

class ParkingProvider(Provider):
    app_factories = provide_all(
        ContractFactory,
        ContractIncomeFactory,
        override=False
    )

    plate_identifier = provide(
        source=DefaultPlateIdentifier,
        provides=PlateIdentifier,
        override=False
    )

    app_services = provide_all(
        SpotAnalyzer,
        VehicleRecognizer,
        override=False
    )

    app_rest_mappers = provide_all(
        RequestIncomeMapper,
        ContractResponseMapper,
        RequestCommandMapper,
        override=False
    )

    app_handlers = provide_all(
        analyze_spot.Handler,
        override=False
    )

    @provide(override=False)
    def make_config_ml(self) -> config.Ml:
        return config.Ml()

    @provide(override=False)
    def make_vehicle_identifier(
        self,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml
    ) -> VehicleIdentifier:
        match config_ml.vehicle_identifier:
            case "default":
                return DefaultVehicleIdentifier()
            case "ml_detection":
                return MlDetectionVehicleIdentifier(
                    self._get_vehicle_identifier_ml_detection_provider(shared_config_ml),
                    config_ml.vehicle_identifier_threshold
                )
            case _:
                raise ValueError(f"Unknown vehicle identifier: {config_ml.vehicle_identifier}")

    @provide(override=False)
    def make_plate_identifier(
        self,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml
    ) -> PlateIdentifier:
        match config_ml.plate_identifier:
            case "default":
                return DefaultPlateIdentifier()
            case "ml_detection":
                return MlDetectionPlateIdentifier(
                    self._get_plate_identifier_ml_detection_provider(shared_config_ml),
                    config_ml.plate_identifier_threshold
                )
            case _:
                raise ValueError(f"Unknown plate identifier: {config_ml.plate_identifier}")

    def _get_vehicle_identifier_ml_detection_provider(
        self,
        config_ml: shared_config.Ml
    ) -> MlDetectionProvider:
        return self._get_ml_detection_provider(
            str(config_ml.yolo_detection_model_path),
            config_ml
        )

    def _get_plate_identifier_ml_detection_provider(
        self,
        config_ml: shared_config.Ml
    ) -> MlDetectionProvider:
        return self._get_ml_detection_provider(
            str(config_ml.yolo_license_plate_detection_model_path),
            config_ml
        )

    def _get_ml_detection_provider(
        self,
        model: str,
        config_ml: shared_config.Ml
    ) -> MlDetectionProvider:
        return YOLOMlDetectionProvider(
            model,
            config_ml.yolo_detection_model_task,
            config_ml.yolo_detection_model_device
        )
