from pydantic import FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict

class ML(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='ml_')

    yolo_detection_model_path: FilePath
