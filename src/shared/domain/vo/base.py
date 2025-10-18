from dataclasses import dataclass
from abc import ABC

from shared.domain.exception.base import ValidationError

class ValueObject(ABC):
    """
    Base class for value objects
    """


@dataclass(frozen=True)
class Id(ValueObject):
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValidationError("ID cannot be empty")

    def __str__(self) -> str:
        return self.value
