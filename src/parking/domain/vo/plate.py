from dataclasses import dataclass
from shared.domain.vo.base import ValueObject

@dataclass(frozen=True)
class Plate(ValueObject):
    value: str
    country: str
