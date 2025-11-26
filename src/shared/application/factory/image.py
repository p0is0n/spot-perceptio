from typing import Protocol

from shared.domain.aggregate.image import Image
from shared.application.dto.contract import income

class ImageFactory(Protocol):
    async def make_from_income(self, image: income.Image, /) -> Image: ...
