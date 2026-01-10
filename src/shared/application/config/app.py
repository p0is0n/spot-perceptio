from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.application.log import Level

class App(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='app_',
        validation_error_cause=True
    )

    debug: bool
    log_level: Level

    @field_validator('log_level', mode='before')
    @classmethod
    def parse_log_level(cls, v: str) -> str | None:
        if not len(v) > 0:
            return Level.INFO

        return Level(v.upper())
