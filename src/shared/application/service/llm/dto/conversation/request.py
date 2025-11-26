from shared.application.dto.base import Base
from shared.application.service.llm.dto.conversation.base import Message

class Model(Base):
    id: str


class Request(Base):
    model: Model
    messages: list[Message]
    max_tokens: int | None = None
    stream: bool | None = None
