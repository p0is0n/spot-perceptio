from typing import Protocol, Self, Any
from pydantic_core.core_schema import any_schema, AnySchema

from shared.domain.vo.coordinate import BoundingBox, RotatedBoundingBox, Polygon

class Binary(Protocol):
    async def data(self) -> bytes: ...
    async def hash(self) -> str: ...

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> AnySchema:
        return any_schema()


class ImageBinary(Binary, Protocol):
    async def crop(
        self,
        coordinate: BoundingBox | RotatedBoundingBox | Polygon,
        /
    ) -> Self: ...
