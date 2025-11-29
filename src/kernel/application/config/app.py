from pydantic_settings import BaseSettings, SettingsConfigDict

class APP(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='app_',
        validation_error_cause=True
    )

    debug: bool = False
 