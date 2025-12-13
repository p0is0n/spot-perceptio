from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Ml(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='ml_',
        validation_error_cause=True
    )

    yolo_model_device: str | None = None

    @field_validator('yolo_model_device', mode='before')
    @classmethod
    def parse_vehicle_identifiers(cls, v: str) -> str | None:
        if not len(v) > 0:
            return None

        return v
