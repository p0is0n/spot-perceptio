from typing import Protocol, Self
from shared.domain.vo.coordinate import BoundingBox

class Binary(Protocol):
    def data(self) -> bytes: ...


class ImageBinary(Binary):
    def crop(self, coordinate: BoundingBox) -> Self: ...
