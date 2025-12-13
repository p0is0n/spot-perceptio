from typing import Annotated

from pydantic import field_validator, Field, FilePath, DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode

class Ml(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='ml_',
        validation_error_cause=True
    )

    vehicle_identifiers: Annotated[tuple[str, ...], NoDecode]
    vehicle_identifier_yolo_model_path: FilePath | DirectoryPath
    vehicle_identifier_yolo_threshold: float = Field(default=0.90, gt=0.0, lt=1.0)

    plate_identifiers: Annotated[tuple[str, ...], NoDecode]
    plate_identifier_yolo_model_path: FilePath | DirectoryPath
    plate_identifier_yolo_threshold: float = Field(default=0.60, gt=0.0, lt=1.0)
    plate_identifier_hyperlpr_threshold: float = Field(default=0.90, gt=0.0, lt=1.0)

    @field_validator('vehicle_identifiers', 'plate_identifiers', mode='before')
    @classmethod
    def parse_vehicle_identifiers(cls, v: str) -> tuple[str, ...]:
        return tuple(
            x.strip() for x in v.split(",") if x.strip()
        )
