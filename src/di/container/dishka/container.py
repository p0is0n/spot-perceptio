from typing import Any

from dishka import AsyncContainer as DiContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka

from fastapi import FastAPI

from di.container.contract import Container as ContractContainer, T

from di.container.dishka.providers.provider import Provider
from di.container.dishka.providers.shared_provider import SharedProvider
from di.container.dishka.providers.kernel_provider import KernelProvider
from di.container.dishka.providers.parking_provider import ParkingProvider

class Container(ContractContainer):

    def __init__(self) -> None:
        self._providers: list[Provider] = self._make_providers()
        self._container: DiContainer | None = None

    def setup(self, app: Any = None, /) -> None:
        self._container = make_async_container(
            *self._providers,
            skip_validation=False
        )

        if app is not None:
            self._setup_app(app)

    async def shutdown(self) -> None:
        if self._container is not None:
            await self._container.close()

    async def get(self, dependency: type[T], /) -> T:
        if self._container is None:
            raise RuntimeError("Container not initialized")

        return await self._container.get(dependency)

    def _setup_app(self, app: Any = None, /) -> None:
        if self._container is None:
            return

        if isinstance(app, FastAPI):
            setup_dishka(self._container, app)

    def _make_providers(self) -> list[Provider]:
        return [
            SharedProvider(),
            KernelProvider(),
            ParkingProvider()
        ]
