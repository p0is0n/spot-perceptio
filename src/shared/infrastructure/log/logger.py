import logging

from typing import Any

from shared.application.log.logger import (
    LogMessage,
    LogData,
    LogTags,
    Logger
)

class DefaultLogger(Logger):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.debug(
            msg,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def info(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.info(
            msg,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def warning(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.warning(
            msg,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def error(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.error(
            msg,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def exception(
        self,
        msg: LogMessage,
        /,
        *,
        exception: BaseException,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.error(
            msg,
            exc_info=exception,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def critical(
        self,
        msg: LogMessage,
        /,
        *,
        data: LogData | None = None,
        tags: LogTags | None = None,
    ) -> None:
        self._logger.critical(
            msg,
            extra=self._make_extra(
                data=data,
                tags=tags
            ),
        )

    def _make_extra(
        self,
        *,
        data: LogData | None,
        tags: LogTags | None,
    ) -> dict[str, Any]:
        extra: dict[str, Any] = {}

        if data is not None:
            extra["data"] = data

        if tags is not None:
            extra["tags"] = tags

        return extra
