from typing import Protocol, Any, TypeVar

T = TypeVar("T")

class Container(Protocol):
    def setup(self, app: Any = None, /) -> None: ...

    async def shutdown(self) -> None: ...

    async def get(self, dependency: type[T], /) -> T: ...
