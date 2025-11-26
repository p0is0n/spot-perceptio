from typing_extensions import Self
from pydantic import HttpUrl, model_validator

from shared.application.dto.base import Base

class Image(Base):
    data: bytes | None = None
    url: HttpUrl | None = None

    @model_validator(mode='after')
    def check_image_provided(self) -> Self:
        if self.data is None and self.url is None:
            raise ValueError("Either data or url must be provided.")

        return self
