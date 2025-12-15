import asyncio

from functools import partial
from concurrent.futures import ThreadPoolExecutor
from typing import ParamSpec, TypeVar
from collections.abc import Callable

from shared.application.tool.worker_pool import WorkerPool

_P = ParamSpec("_P")
_R = TypeVar("_R")

class AsyncIOThreadWorkerPool(WorkerPool):
    def __init__(self, *, max_workers: int) -> None:
        self._executor = ThreadPoolExecutor()
        self._semaphore = asyncio.Semaphore(max_workers)

    async def run(
        self,
        func: Callable[_P, _R],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R:
        async with self._semaphore:
            loop = asyncio.get_running_loop()

            return await loop.run_in_executor(
                self._executor,
                partial(func, *args, **kwargs)
            )

    async def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
