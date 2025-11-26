from shared.application.handler.base.command import Base
from kernel.application.system.dto.echo import EchoValue

class Command(Base):
    value: EchoValue
