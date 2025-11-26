from typing import Protocol
from datetime import datetime

class DateTimeFactory(Protocol):
    def make_current(self) -> datetime: ...
