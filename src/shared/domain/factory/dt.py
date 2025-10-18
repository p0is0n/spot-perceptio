from typing import Protocol
from datetime import datetime

class DatetimeFactory(Protocol):
    def make_current(self) -> datetime: ...
