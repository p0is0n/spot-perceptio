from enum import Enum
from pydantic import BaseModel

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageContent(BaseModel):
    type: str


class Message(BaseModel):
    role: MessageRole
    content: list[MessageContent]
