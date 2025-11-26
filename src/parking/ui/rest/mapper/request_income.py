from shared.application.dto.contract import income as shared_income

from parking.application.dto.contract import income
from parking.ui.rest.request.image import ImageRequest
from parking.ui.rest.request.spot import SpotRequest
from parking.ui.rest.request.coordinate import CoordinateRequest, PolygonRequest

class RequestIncomeMapper:
    def make_image(
        self,
        image: ImageRequest,
        /
    ) -> shared_income.Image:
        return shared_income.Image(
            data=image.data,
            url=image.url
        )

    def make_spot(
        self,
        spot: SpotRequest,
        /
    ) -> income.Spot:
        coordinate = self.make_polygon_coordinate(spot.coordinate)

        return income.Spot(
            id=spot.id,
            coordinate=coordinate
        )

    def make_coordinate(
        self,
        coordinate: CoordinateRequest,
        /
    ) -> income.Coordinate:
        return income.Coordinate(
            x=coordinate.x,
            y=coordinate.y
        )

    def make_polygon_coordinate(
        self,
        coordinate: PolygonRequest,
        /
    ) -> income.Polygon:
        corners = tuple(
            self.make_coordinate(corner) for corner in coordinate.corners
        )

        return income.Polygon(
            corners=corners
        )
