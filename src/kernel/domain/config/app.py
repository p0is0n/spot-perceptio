from pydantic_settings import BaseSettings, SettingsConfigDict

class APP(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='app_')

    debug: bool
