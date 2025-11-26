from shared.application.dto.base import Base

from parking.application.dto.contract.income.coordinate import Polygon

class Spot(Base):
    id: str
    coordinate: Polygon
