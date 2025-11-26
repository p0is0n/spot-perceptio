from shared.domain.aggregate.base import Aggregate
from shared.domain.vo.base import Id
from shared.domain.vo.coordinate import Polygon

class Spot(Aggregate):
    id: Id
    coordinate: Polygon
