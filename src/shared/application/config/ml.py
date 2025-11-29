from pydantic import FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict

class Ml(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        env_prefix='ml_',
        validation_error_cause=True
    )

    yolo_detection_model_path: FilePath
    yolo_detection_model_task: str = "detect"
    yolo_detection_model_device: str | None = None
