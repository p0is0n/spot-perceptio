from shared.application.log import Logger
from shared.domain.factory.dt import DateTimeFactory

from kernel.application.system.handler.check_health.query import Query
from kernel.application.system.dto.health import Health
from kernel.application.system.dto.health_status import HealthStatus

class Handler:
    def __init__(
        self,
        *,
        dt: DateTimeFactory,
        logger: Logger
    ) -> None:
        self._dt = dt
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={},
            tags=("handler_system_check_health", "init"),
        )

    async def handle(self, query: Query, /) -> Health:
        self._logger.debug(
            "Handle query",
            data={},
            tags=("handler_system_check_health", "handle"),
        )

        result = Health(
            status=HealthStatus.SUCCESS,
            time=self._dt.make_current()
        )

        self._logger.debug(
            "Handle query finished",
            data={
                "health_status": result.status.value,
                "health_time": result.time.isoformat(),
            },
            tags=("handler_system_check_health", "handle"),
        )

        return result
