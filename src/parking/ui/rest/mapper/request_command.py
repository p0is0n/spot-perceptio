from parking.application.handler import analyze_spot
from parking.application.handler import analyze_spots

from parking.ui.rest.mapper.request_income import RequestIncomeMapper
from parking.ui.rest.request.analyze_spot import AnalyzeSpotRequest
from parking.ui.rest.request.analyze_spots import AnalyzeSpotsRequest

class RequestCommandMapper:
    def __init__(self, request_mapper: RequestIncomeMapper) -> None:
        self._request_mapper = request_mapper

    def make_analyze_spot(
        self,
        request: AnalyzeSpotRequest,
        /
    ) -> analyze_spot.Command:
        image = self._request_mapper.make_image(request.image)
        spot = self._request_mapper.make_spot(request.spot)

        return analyze_spot.Command(
            image=image,
            spot=spot
        )

    def make_analyze_spots(
        self,
        request: AnalyzeSpotsRequest,
        /
    ) -> analyze_spots.Command:
        image = self._request_mapper.make_image(request.image)
        spots = self._request_mapper.make_spots(request.spots)

        return analyze_spots.Command(
            image=image,
            spots=spots
        )
