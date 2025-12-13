from pathlib import Path
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
from parking.infrastructure.provider.vehicle.yolo_identifier import (
    YOLOVehicleIdentifier
)
from parking.infrastructure.provider.plate.identifier import DefaultPlateIdentifier
from parking.infrastructure.provider.plate.yolo_identifier import (
    YOLOPlateIdentifier
)
from parking.infrastructure.provider.plate.hyperlpr_identifier import (
    HyperlprPlateIdentifier
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
        return DefaultVehicleIdentifier(tuple(
            self._make_vehicle_identifier_by_name(
                identifier,
                config_ml,
                shared_config_ml
            )
            for identifier in config_ml.vehicle_identifiers
        ))

    @provide(override=False)
    def make_plate_identifier(
        self,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml
    ) -> PlateIdentifier:
        return DefaultPlateIdentifier(tuple(
            self._make_plate_identifier_by_name(
                identifier,
                config_ml,
                shared_config_ml
            )
            for identifier in config_ml.plate_identifiers
        ))

    def _make_vehicle_identifier_by_name(
        self,
        identifier: str,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml,
        /
    ) -> VehicleIdentifier:
        match identifier:
            case "yolo":
                return YOLOVehicleIdentifier(
                    self._get_vehicle_identifier_yolo_detection_provider(
                        config_ml,
                        shared_config_ml
                    ),
                    config_ml.vehicle_identifier_yolo_threshold
                )
            case _:
                raise ValueError(f"Unknown vehicle identifier: {identifier}")

    def _make_plate_identifier_by_name(
        self,
        identifier: str,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml,
        /
    ) -> PlateIdentifier:
        match identifier:
            case "yolo":
                return YOLOPlateIdentifier(
                    self._get_plate_identifier_yolo_detection_provider(
                        config_ml,
                        shared_config_ml
                    ),
                    config_ml.plate_identifier_yolo_threshold
                )
            case "hyperlpr":
                return HyperlprPlateIdentifier(
                    config_ml.plate_identifier_hyperlpr_threshold
                )
            case _:
                raise ValueError(f"Unknown plate identifier: {identifier}")

    def _get_vehicle_identifier_yolo_detection_provider(
        self,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml,
        /
    ) -> MlDetectionProvider:
        return self._get_yolo_detection_provider(
            config_ml.vehicle_identifier_yolo_model_path,
            shared_config_ml
        )

    def _get_plate_identifier_yolo_detection_provider(
        self,
        config_ml: config.Ml,
        shared_config_ml: shared_config.Ml,
        /
    ) -> MlDetectionProvider:
        return self._get_yolo_detection_provider(
            config_ml.plate_identifier_yolo_model_path,
            shared_config_ml
        )

    def _get_yolo_detection_provider(
        self,
        model: Path,
        config_ml: shared_config.Ml,
        /
    ) -> MlDetectionProvider:
        return YOLOMlDetectionProvider(
            model,
            "detect",
            config_ml.yolo_model_device
        )
