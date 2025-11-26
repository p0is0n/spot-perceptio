from shared.application.factory.image import ImageFactory

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.application.factory.contract import ContractFactory
from parking.application.factory.contract_income import ContractIncomeFactory
from parking.application.dto.contract.spot import ParkingSpot
from parking.application.handler.analyze_spot.command import Command

class Handler:
    def __init__(
        self,
        spot_analyzer: SpotAnalyzer,
        contract_factory: ContractFactory,
        contract_income_factory: ContractIncomeFactory,
        image_factory: ImageFactory
    ) -> None:
        self._spot_analyzer = spot_analyzer
        self._contract_factory = contract_factory
        self._contract_income_factory = contract_income_factory
        self._image_factory = image_factory

    async def handle(self, command: Command, /) -> ParkingSpot:
        image = await self._image_factory.make_from_income(command.image)
        spot = self._contract_income_factory.make_spot(command.spot)

        parking_spot = await self._spot_analyzer.analyze(image, spot)
        parking_spot_contract = self._contract_factory.make_parking_spot(parking_spot)

        return parking_spot_contract
