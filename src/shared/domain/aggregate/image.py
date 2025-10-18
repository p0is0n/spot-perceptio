from typing import Self
from dataclasses import dataclass

from shared.domain.vo.coordinate import BoundingBox
from shared.domain.vo.data import ImageBinary

@dataclass(frozen=True)
class Image:
    data: ImageBinary
    coordinate: BoundingBox

    def crop(self, coordinate: BoundingBox) -> Self:
        return Image(
            data=self.data.crop(coordinate),
            coordinate=coordinate
        )
