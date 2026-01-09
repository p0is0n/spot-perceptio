import logging
import sys

from dishka import provide, provide_all

from di.container.dishka.providers.provider import Provider

from shared.domain.factory.dt import DateTimeFactory

from shared.application import config
from shared.application.log import Logger

from shared.application.factory.tool.worker_pool import WorkerPoolFactory

from shared.application.tool.worker_pool import WorkerPool
from shared.application.tool.image_similarity import ImageSimilarity

from shared.application.http.client.protocol import ClientProtocol as HttpClientProtocol
from shared.application.factory.image import ImageFactory
from shared.application.service.llm.provider import LLMProvider

from shared.infrastructure.log.logger import DefaultLogger

from shared.infrastructure.http.client.httpx_protocol import HttpxClientProtocol

from shared.infrastructure.factory.tool.worker_pool import DefaultWorkerPoolFactory
from shared.infrastructure.factory.dt import DefaultDateTimeFactory
from shared.infrastructure.factory.image import Cv2ImageFactory

from shared.infrastructure.service.llm.provider import OpenAILLMProvider
from shared.infrastructure.service.ml.factory.yolo_provider import YOLOMlDetectionFactory

from shared.infrastructure.tool.image_similarity.image_similarity import ImageSimilarityEvaluator
from shared.infrastructure.tool.image_similarity.dhash_similarity import DHashSimilarity
from shared.infrastructure.tool.image_similarity.phash_similarity import PHashSimilarity

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
    def make_logger(self) -> Logger:
        logger_provider = self._create_logger(
            name="app"
        )
        logger: Logger = DefaultLogger(logger_provider)

        return logger

    @provide(override=False)
    def make_worker_pool(
        self,
        worker_pool_factory: WorkerPoolFactory
    ) -> WorkerPool:
        return worker_pool_factory.make()

    @provide(override=False)
    def make_image_similarity(
        self,
        worker_pool: WorkerPool,
        logger: Logger
    ) -> ImageSimilarity:
        return ImageSimilarityEvaluator(
            (
                DHashSimilarity(worker_pool, logger),
                PHashSimilarity(worker_pool, logger),
            ),
            logger
        )

    @provide(override=False)
    def make_config_ml(self) -> config.Ml:
        return config.Ml()

    def _create_logger(
        self,
        *,
        name: str,
        level: int = logging.DEBUG,
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if logger.handlers:
            raise ValueError("Logger already has handlers")

        logger.addHandler(self._make_logger_handler(level))
        logger.propagate = False

        for library_name in (
            "ultralytics",
            "fastapi",
        ):
            library_logger = logging.getLogger(library_name)
            library_logger.setLevel(logging.DEBUG)
            library_logger.handlers.clear()
            library_logger.propagate = True

            for handler in list(logger.handlers):
                library_logger.addHandler(handler)

        return logger

    def _make_logger_handler(self, level: int, /) -> logging.Handler:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(self._make_logger_formatter())

        return handler

    def _make_logger_formatter(self) -> logging.Formatter:
        datefmt: str = "%Y-%m-%dT%H:%M:%S%z"
        fmt: str = (
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s "
            "data=%(data)s "
            "tags=%(tags)s"
        )

        return logging.Formatter(
            fmt,
            datefmt,
            defaults={
                "data": {},
                "tags": ()
            }
        )
