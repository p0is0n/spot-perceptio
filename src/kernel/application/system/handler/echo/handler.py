from shared.domain.factory.dt import DateTimeFactory

from kernel.application.system.handler.echo.command import Command
from kernel.application.system.dto.echo import Echo

class Handler:
    def __init__(self, dt: DateTimeFactory) -> None:
        self._dt = dt

    async def handle(self, command: Command, /) -> Echo:
        return Echo(
            echo=command.value,
            time=self._dt.make_current()
        )
