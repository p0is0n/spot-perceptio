from typing import Protocol, TypeVar, ParamSpec
from collections.abc import Callable

_P = ParamSpec("_P")
_R = TypeVar("_R")

class WorkerPool(Protocol):
    async def run(
        self,
        func: Callable[_P, _R],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R: ...

    async def shutdown(self) -> None: ...
