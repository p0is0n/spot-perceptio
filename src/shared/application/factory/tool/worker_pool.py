from typing import Protocol

from shared.application.tool.worker_pool import WorkerPool

class WorkerPoolFactory(Protocol):
    def make(self) -> WorkerPool: ...
    def make_with_limits(self, *, max_workers: int) -> WorkerPool: ...
