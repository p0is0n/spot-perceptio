from shared.application.dto.base import Base
from shared.application.service.ml.dto.detection.box import Box

class Response(Base):
    id: str | None = None
    boxes: tuple[Box, ...]
