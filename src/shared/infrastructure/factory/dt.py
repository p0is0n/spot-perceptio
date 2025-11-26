from datetime import datetime, UTC
from shared.domain.factory.dt import DateTimeFactory

class DefaultDateTimeFactory(DateTimeFactory):
    def make_current(self) -> datetime:
        return datetime.now(UTC)
