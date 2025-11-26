import asyncio

from concurrent.futures import ThreadPoolExecutor
from typing import Any
from collections.abc import Callable

from shared.application.tool.worker_pool import WorkerPool

class AsyncIOThreadWorkerPool(WorkerPool):
    def __init__(self, *, max_workers: int) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run(self, func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self._executor,
            lambda: func(*args, **kwargs)
        )

        return result

    async def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
