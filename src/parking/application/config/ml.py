from pydantic import PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict

class Ml(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='ml_',
        validation_error_cause=True
    )

    vehicle_identifier_threshold: PositiveFloat
