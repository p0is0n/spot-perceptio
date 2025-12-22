from dishka import provide, provide_all

from di.container.dishka.providers.provider import Provider

from shared.application.tool.image_cache import ImageCache
from shared.application.tool.image_similarity import ImageSimilarity

from shared.infrastructure.tool.image_cache.similarity_image_cache import SimilarityImageCache

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.service.vehicle.recognizer import VehicleRecognizer
from parking.domain.provider.vehicle.identifier import VehicleIdentifier
from parking.domain.provider.plate.identifier import PlateIdentifier

from parking.application import config
from parking.application.factory.contract import ContractFactory
from parking.application.factory.contract_income import ContractIncomeFactory
from parking.application.handler import analyze_spot

from parking.infrastructure.provider.vehicle.identifier import DefaultVehicleIdentifier
from parking.infrastructure.provider.vehicle.cache_identifier import (
    CacheVehicleIdentifier,
    CacheVehicleIdentifierResult
)

from parking.infrastructure.provider.plate.identifier import DefaultPlateIdentifier
from parking.infrastructure.provider.plate.cache_identifier import (
    CachePlateIdentifier,
    CachePlateIdentifierResult
)

from parking.infrastructure.factory.vehicle.identifier import VehicleIdentifierFactory
from parking.infrastructure.factory.plate.identifier import PlateIdentifierFactory

from parking.ui.rest.mapper.request_income import RequestIncomeMapper
from parking.ui.rest.mapper.contract_response import ContractResponseMapper
from parking.ui.rest.mapper.request_command import RequestCommandMapper

class ParkingProvider(Provider):
    app_factories = provide_all(
        ContractFactory,
        ContractIncomeFactory,
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

    infra_factories = provide_all(
        VehicleIdentifierFactory,
        PlateIdentifierFactory,
        override=False
    )

    @provide(override=False)
    def make_config_ml(self) -> config.Ml:
        return config.Ml()

    @provide(override=False)
    def make_vehicle_identifier(
        self,
        config_ml: config.Ml,
        vehicle_identifier_factory: VehicleIdentifierFactory,
        image_cache: ImageCache[CacheVehicleIdentifierResult]
    ) -> VehicleIdentifier:
        default_identifier = DefaultVehicleIdentifier(
            vehicle_identifier_factory.make_all()
        )
        if not config_ml.vehicle_identifier_cache:
            return default_identifier

        return CacheVehicleIdentifier(
            default_identifier,
            image_cache
        )

    @provide(override=False)
    def make_plate_identifier(
        self,
        config_ml: config.Ml,
        plate_identifier_factory: PlateIdentifierFactory,
        image_cache: ImageCache[CachePlateIdentifierResult]
    ) -> PlateIdentifier:
        default_identifier = DefaultPlateIdentifier(
            plate_identifier_factory.make_all()
        )
        if not config_ml.plate_identifier_cache:
            return default_identifier

        return CachePlateIdentifier(
            default_identifier,
            image_cache
        )

    @provide(override=False)
    def make_vehicle_identifier_image_cache(
        self,
        config_ml: config.Ml,
        similarity: ImageSimilarity
    ) -> ImageCache[CacheVehicleIdentifierResult]:
        return SimilarityImageCache(
            max_size=1000,
            tolerance=config_ml.vehicle_identifier_cache_tolerance,
            similarity=similarity
        )

    @provide(override=False)
    def make_plate_identifier_image_cache(
        self,
        config_ml: config.Ml,
        similarity: ImageSimilarity
    ) -> ImageCache[CachePlateIdentifierResult]:
        return SimilarityImageCache(
            max_size=1000,
            tolerance=config_ml.plate_identifier_cache_tolerance,
            similarity=similarity
        )
