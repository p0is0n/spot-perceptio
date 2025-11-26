from abc import ABC
from pydantic import BaseModel, ConfigDict

class Aggregate(BaseModel, ABC):
    model_config = ConfigDict(frozen=True)
