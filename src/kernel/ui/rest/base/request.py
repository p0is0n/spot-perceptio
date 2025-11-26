from pydantic import BaseModel, ConfigDict

class BaseRequest(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")
