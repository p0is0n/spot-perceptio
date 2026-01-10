from typing import Protocol, TypeVar
from collections.abc import Awaitable
from datetime import timedelta

_R = TypeVar("_R")

class WorkerParallel(Protocol):
    async def run(
        self,
        *awaitables: Awaitable[_R],
        timeout: timedelta | None = None
    ) -> tuple[_R, ...]: ...
