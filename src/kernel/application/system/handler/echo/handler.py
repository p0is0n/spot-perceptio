from shared.application.log import Logger
from shared.domain.factory.dt import DateTimeFactory

from kernel.application.system.handler.echo.command import Command
from kernel.application.system.dto.echo import Echo

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
            tags=("handler_system_echo", "init"),
        )

    async def handle(self, command: Command, /) -> Echo:
        self._logger.debug(
            "Handle command",
            data={},
            tags=("handler_system_echo", "handle"),
        )

        result = Echo(
            echo=command.value,
            time=self._dt.make_current()
        )

        self._logger.debug(
            "Handle command finished",
            data={
                "echo_value": result.echo,
                "echo_time": result.time.isoformat(),
            },
            tags=("handler_system_echo", "handle"),
        )

        return result
