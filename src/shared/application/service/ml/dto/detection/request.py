from pydantic import NonNegativeInt, NonNegativeFloat

from shared.domain.aggregate.image import Image
from shared.application.dto.base import Base
from shared.application.service.ml.dto.detection.box import Type

class Request(Base):
    source: Image
    image_size: NonNegativeInt | None = None
    score_threshold: NonNegativeFloat | None = None
    target_types: tuple[Type, ...] | None = None
