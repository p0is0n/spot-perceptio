from typing import Annotated
from pydantic import AwareDatetime
from pydantic.types import StringConstraints

from shared.application.dto.base import Base

EchoValue = Annotated[str, StringConstraints(
    pattern=r"^[a-zA-Z]+$",
    min_length=1,
    max_length=100,
    strict=True
)]

class Echo(Base):
    echo: EchoValue
    time: AwareDatetime
