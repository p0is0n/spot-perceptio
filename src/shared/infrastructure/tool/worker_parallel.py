import asyncio

from typing import TypeVar
from collections.abc import Awaitable
from datetime import timedelta

from shared.application.tool.worker_parallel import WorkerParallel

_R = TypeVar("_R")

class AsyncIOWorkerParallel(WorkerParallel):
    async def run(
        self,
        *awaitables: Awaitable[_R],
        timeout: timedelta | None = None
    ) -> tuple[_R, ...]:
        gathered = asyncio.gather(*awaitables)
        if timeout is None:
            result = await gathered
        else:
            result = await asyncio.wait_for(gathered, timeout=timeout.total_seconds())

        return tuple(result)
