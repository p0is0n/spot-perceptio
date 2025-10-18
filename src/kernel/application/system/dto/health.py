from pydantic import BaseModel, AwareDatetime
from kernel.application.system.dto.health_status import HealthStatus

class Health(BaseModel):
    status: HealthStatus
    time: AwareDatetime
