from shared.domain.factory.dt import DateTimeFactory

from kernel.application.system.handler.check_health.query import Query
from kernel.application.system.dto.health import Health
from kernel.application.system.dto.health_status import HealthStatus

class Handler:
    def __init__(self, dt: DateTimeFactory) -> None:
        self._dt = dt

    async def handle(self, query: Query, /) -> Health:
        return Health(
            status=HealthStatus.SUCCESS,
            time=self._dt.make_current()
        )
