from datetime import datetime, UTC
from shared.domain.factory.dt import DatetimeFactory

class DefaultDatetimeFactory(DatetimeFactory):
    def make_current(self) -> datetime:
        return datetime.now(UTC)
