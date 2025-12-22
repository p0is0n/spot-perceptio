from typing import ParamSpec, TypeVar
from collections.abc import Callable

from shared.application.tool.worker_pool import WorkerPool

_P = ParamSpec("_P")
_R = TypeVar("_R")

class NoopWorkerPool(WorkerPool):
    async def run(
        self,
        func: Callable[_P, _R],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R:
        return func(*args, **kwargs)

    async def shutdown(self) -> None:
        pass
