from dishka import provide, provide_all

from di.container.dishka.providers.provider import Provider

from shared.application.service.ml.provider.detection import MlDetectionProvider

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.service.vehicle.recognizer import VehicleRecognizer
from parking.domain.provider.vehicle.identifier import VehicleIdentifier
from parking.domain.provider.plate.identifier import PlateIdentifier

from parking.application import config
from parking.application.factory.contract import ContractFactory
from parking.application.factory.contract_income import ContractIncomeFactory
from parking.application.handler import analyze_spot

from parking.infrastructure.provider.vehicle.ml_detection_identifier import (
    MlDetectionVehicleIdentifier
)
from parking.infrastructure.provider.plate.identifier import DefaultPlateIdentifier

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
        provider: MlDetectionProvider,
        config_ml: config.Ml
    ) -> VehicleIdentifier:
        return MlDetectionVehicleIdentifier(
            provider,
            config_ml.vehicle_identifier_threshold
        )
