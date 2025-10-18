from typing import Any

from dishka import (
    AsyncContainer as DiContainer,
    Provider as DiProvider,
    Scope,
    provide,
    provide_all,
    make_async_container
)

from dishka.integrations.fastapi import setup_dishka

from fastapi import FastAPI

from di.container.contract import Container as ContractContainer

from shared.domain.factory.dt import DatetimeFactory
from shared.application.factory.tool.worker_pool import WorkerPoolFactory
from shared.infrastructure.factory.tool.worker_pool import DefaultWorkerPoolFactory
from shared.infrastructure.factory.dt import DefaultDatetimeFactory
from shared.application.service.llm.provider import LLMProvider
from shared.infrastructure.service.llm.provider import OpenAILLMProvider

from kernel.application.system.handler import check_health
from kernel.application.system.handler import echo

class ContainerProvider(DiProvider):
    scope = Scope.APP

    datetime_factory = provide(
        source=DefaultDatetimeFactory,
        provides=DatetimeFactory,
        override=False
    )

    worker_pool_factory = provide(
        source=DefaultWorkerPoolFactory,
        provides=WorkerPoolFactory,
        override=False
    )

    llm_provider = provide(
        source=OpenAILLMProvider,
        provides=LLMProvider,
        override=False
    )

    handlers = provide_all(
        check_health.Handler,
        echo.Handler,
        override=False
    )


class Container(ContractContainer):

    def __init__(self) -> None:
        self.provider: ContainerProvider = ContainerProvider()
        self.container: DiContainer | None = None

    def setup(self, app: Any = None):
        self.container = make_async_container(
            self.provider,
            skip_validation=False
        )

        if app is not None:
            if isinstance(app, FastAPI):
                setup_dishka(self.container, app)

    def shutdown(self) -> None:
        pass
