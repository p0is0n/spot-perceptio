from typing import Self

from shared.domain.aggregate.base import Aggregate
from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox, Polygon
from shared.domain.vo.data import ImageBinary

class Image(Aggregate):
    data: ImageBinary
    coordinate: BoundingBox | RotatedBoundingBox | Polygon

    async def crop(
        self,
        coordinate: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> Self:
        cropped = await self.data.crop(coordinate)

        return type(self)(
            data=cropped,
            coordinate=coordinate
        )
