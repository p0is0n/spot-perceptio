from dishka import provide

from di.container.dishka.providers.provider import Provider

from shared.domain.factory.dt import DateTimeFactory

from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.application.factory.image import ImageFactory
from shared.application.service.ml.provider.detection import MLDetectionProvider
from shared.application.service.llm.provider import LLMProvider

from shared.infrastructure.factory.tool.worker_pool import DefaultWorkerPoolFactory
from shared.infrastructure.factory.dt import DefaultDateTimeFactory
from shared.infrastructure.factory.image import Cv2ImageFactory
from shared.infrastructure.service.ml.provider.yolo_provider import YOLOMLDetectionProvider
from shared.infrastructure.service.llm.provider import OpenAILLMProvider

class SharedProvider(Provider):
    domain_datetime_factory = provide(
        source=DefaultDateTimeFactory,
        provides=DateTimeFactory,
        override=False
    )

    app_worker_pool_factory = provide(
        source=DefaultWorkerPoolFactory,
        provides=WorkerPoolFactory,
        override=False
    )

    app_image_factory = provide(
        source=Cv2ImageFactory,
        provides=ImageFactory,
        override=False
    )

    app_llm_provider = provide(
        source=OpenAILLMProvider,
        provides=LLMProvider,
        override=False
    )

    @provide(override=False)
    def make_ml_detection_provider(self) -> MLDetectionProvider:
        return YOLOMLDetectionProvider("/app/models/yolo/yolo11n.pt")
