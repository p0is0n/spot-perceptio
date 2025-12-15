from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.application.tool.worker_pool import WorkerPool
from shared.infrastructure.tool.worker_pool import AsyncIOThreadWorkerPool

class DefaultWorkerPoolFactory(WorkerPoolFactory):
    def make(self) -> WorkerPool:
        return AsyncIOThreadWorkerPool(
            max_workers=10
        )

    def make_with_limits(self, *, max_workers: int) -> WorkerPool:
        return AsyncIOThreadWorkerPool(
            max_workers=max_workers
        )
