from shared.domain.vo.base import Id
from shared.domain.vo.coordinate import Coordinate, BoundingBox, Polygon
from shared.domain.aggregate.spot import Spot

from parking.application.dto.contract import income

class ContractIncomeFactory:
    def make_spot(self, spot: income.Spot, /) -> Spot:
        coordinate = self.make_polygon_coordinate(spot.coordinate)

        return Spot(
            id=Id(value=spot.id),
            coordinate=coordinate
        )

    def make_coordinate(self, coordinate: income.Coordinate, /) -> Coordinate:
        return Coordinate(
            x=coordinate.x,
            y=coordinate.y
        )

    def make_bounding_box_coordinate(self, coordinate: income.BoundingBox, /) -> BoundingBox:
        return BoundingBox(
            p1=self.make_coordinate(coordinate.p1),
            p2=self.make_coordinate(coordinate.p2)
        )

    def make_polygon_coordinate(self, coordinate: income.Polygon, /) -> Polygon:
        corners = tuple(
            self.make_coordinate(corner) for corner in coordinate.corners
        )

        return Polygon(
            corners=corners
        )
