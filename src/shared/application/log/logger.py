from typing import Protocol, TypeAlias
from collections.abc import Mapping

LogMessage: TypeAlias = str
LogPrimitive: TypeAlias = str | int | float | bool | None
LogValue: TypeAlias = (
    LogPrimitive
    | list["LogValue"]
    | dict[str, "LogValue"]
)

LogData: TypeAlias = Mapping[str, LogValue]
LogTags: TypeAlias = tuple[str, ...]

class Logger(Protocol):
    def debug(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...

    def info(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...

    def warning(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...

    def error(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...

    def exception(
        self,
        msg: LogMessage,
        /,
        *,
        exception: BaseException,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...

    def critical(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None: ...
