from typing import Protocol

from shared.domain.aggregate.image import Image

class ImageSimilarity(Protocol):
    async def similar(
        self,
        image1: Image,
        image2: Image,
        /,
        tolerance: float
    ) -> bool: ...
