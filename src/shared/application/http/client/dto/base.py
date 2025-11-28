from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class Data(Generic[T]):
    value: T


class TextData(Data[str]):
    pass


class JsonData(Data[dict[str, Any] | list[Any]]):
    pass


class BinaryData(Data[bytes]):
    pass
