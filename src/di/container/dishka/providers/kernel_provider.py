from dishka import provide_all

from di.container.dishka.providers.provider import Provider

from kernel.application.system.handler import check_health
from kernel.application.system.handler import echo

class KernelProvider(Provider):
    app_handlers = provide_all(
        check_health.Handler,
        echo.Handler,
        override=False
    )
