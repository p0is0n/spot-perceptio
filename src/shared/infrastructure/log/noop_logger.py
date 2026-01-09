from shared.application.log.logger import (
    LogMessage,
    LogData,
    LogTags,
    Logger
)

class NoopLogger(Logger):
    def debug(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass

    def info(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass

    def warning(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass

    def error(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass

    def exception(
        self,
        msg: LogMessage,
        /,
        *,
        exception: BaseException,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass

    def critical(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        pass
