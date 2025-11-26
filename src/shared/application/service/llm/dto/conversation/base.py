from enum import Enum
from shared.application.dto.base import Base

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageContent(Base):
    type: str


class Message(Base):
    role: MessageRole
    content: list[MessageContent]
