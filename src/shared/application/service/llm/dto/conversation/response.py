from shared.application.dto.base import Base
from shared.application.service.llm.dto.conversation.base import Message

class Choice(Base):
    index: float
    message: Message


class Response(Base):
    id: str | None = None
    choices: list[Choice]
