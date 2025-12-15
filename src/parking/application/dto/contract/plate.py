from shared.application.dto.base import Base

from parking.application.dto.contract.coordinate import Polygon

class Plate(Base):
    value: str
    country: str
    coordinate: Polygon
