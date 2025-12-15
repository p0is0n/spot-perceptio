from pathlib import Path

from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.infrastructure.service.ml.provider.yolo_provider import YOLOMlDetectionProvider

class YOLOMlDetectionFactory:
    def __init__(
        self,
        worker_pool_factory: WorkerPoolFactory,
        /
    ) -> None:
        self._worker_pool_factory = worker_pool_factory

    def make(
        self,
        model: Path,
        task: str = "detect",
        device: str | None = None
    ) -> YOLOMlDetectionProvider:
        return YOLOMlDetectionProvider(
            self._worker_pool_factory,
            model,
            task,
            device
        )
