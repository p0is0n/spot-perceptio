from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Ml(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='ml_',
        validation_error_cause=True
    )

    vehicle_identifier: str
    vehicle_identifier_threshold: float = Field(gt=0.0, lt=1.0)

    plate_identifier: str
    plate_identifier_threshold: float = Field(gt=0.0, lt=1.0)
