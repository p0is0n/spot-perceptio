from pydantic_settings import BaseSettings, SettingsConfigDict

class App(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='app_',
        validation_error_cause=True
    )
