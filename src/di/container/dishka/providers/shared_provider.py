from dishka import provide, provide_all

from di.container.dishka.providers.provider import Provider

from shared.domain.factory.dt import DateTimeFactory

from shared.application import config
from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.application.tool.worker_pool import WorkerPool
from shared.application.http.client.protocol import ClientProtocol as HttpClientProtocol
from shared.application.factory.image import ImageFactory
from shared.application.service.llm.provider import LLMProvider

from shared.infrastructure.factory.tool.worker_pool import DefaultWorkerPoolFactory
from shared.infrastructure.http.client.httpx_protocol import HttpxClientProtocol
from shared.infrastructure.factory.dt import DefaultDateTimeFactory
from shared.infrastructure.factory.image import Cv2ImageFactory
from shared.infrastructure.service.llm.provider import OpenAILLMProvider
from shared.infrastructure.service.ml.factory.yolo_provider import YOLOMlDetectionFactory

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

    app_http_client_protocol = provide(
        source=HttpxClientProtocol,
        provides=HttpClientProtocol,
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

    infra_factories = provide_all(
        YOLOMlDetectionFactory,
        override=False
    )

    @provide(override=False)
    def make_worker_pool(
        self,
        worker_pool_factory: WorkerPoolFactory
    ) -> WorkerPool:
        return worker_pool_factory.make()

    @provide(override=False)
    def make_config_ml(self) -> config.Ml:
        return config.Ml()
