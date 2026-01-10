from shared.domain.aggregate.image import Image

from shared.application.log import Logger
from shared.application.factory.image import ImageFactory
from shared.application.tool.worker_parallel import WorkerParallel

from parking.domain.service.spot.analyzer import SpotAnalyzer

from parking.application.factory.contract import ContractFactory
from parking.application.factory.contract_income import ContractIncomeFactory
from parking.application.dto.contract import income
from parking.application.dto.contract.spot import ParkingSpot, ParkingSpots
from parking.application.handler.analyze_spots.command import Command

class Handler:
    def __init__(
        self,
        *,
        spot_analyzer: SpotAnalyzer,
        contract_factory: ContractFactory,
        contract_income_factory: ContractIncomeFactory,
        image_factory: ImageFactory,
        worker_parallel: WorkerParallel,
        logger: Logger,
    ) -> None:
        self._spot_analyzer = spot_analyzer
        self._contract_factory = contract_factory
        self._contract_income_factory = contract_income_factory
        self._image_factory = image_factory
        self._worker_parallel = worker_parallel
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={},
            tags=("handler_analyze_spots", "init"),
        )

    async def handle(self, command: Command, /) -> ParkingSpots:
        self._logger.debug(
            "Handle command",
            data={
                "image_source": "data" if command.image.data else "url",
                "spots_ids": [spot.id for spot in command.spots],
            },
            tags=("handler_analyze_spots", "handle"),
        )

        image = await self._image_factory.make_from_income(command.image)
        parking_spots_contract: tuple[ParkingSpot, ...] = await self._worker_parallel.run(*(
            self._analyze_spot(image, spot) for spot in command.spots
        ))

        self._logger.debug(
            "Handle command finished",
            data={
                "image": await image.fingerprint(),
                "spots_ids": [spot.id for spot in command.spots],
            },
            tags=("handler_analyze_spots", "handle"),
        )

        return ParkingSpots(spots=parking_spots_contract)

    async def _analyze_spot(
        self,
        image: Image,
        income_spot: income.Spot,
        /
    ) -> ParkingSpot:
        spot = self._contract_income_factory.make_spot(income_spot)

        parking_spot = await self._spot_analyzer.analyze(image, spot)
        parking_spot_contract = self._contract_factory.make_parking_spot(parking_spot)

        return parking_spot_contract
