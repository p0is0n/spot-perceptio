from shared.application.handler.base.command import Base
from shared.application.dto.contract.income import Image

from parking.application.dto.contract.income import Spot

class Command(Base):
    image: Image
    spot: Spot
