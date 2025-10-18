from shared.domain.factory.dt import DatetimeFactory
from kernel.application.system.handler.echo.query import Query
from kernel.application.system.dto.echo import Echo

class Handler:
    def __init__(self, dt: DatetimeFactory) -> None:
        self.dt = dt

    async def handle(self, query: Query) -> Echo:
        return Echo(
            echo=query.value,
            time=self.dt.make_current()
        )
