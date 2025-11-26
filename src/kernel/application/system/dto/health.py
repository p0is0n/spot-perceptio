from pydantic import AwareDatetime
from shared.application.dto.base import Base
from kernel.application.system.dto.health_status import HealthStatus

class Health(Base):
    status: HealthStatus
    time: AwareDatetime
