from pydantic import BaseModel

from shared.application.service.llm.dto.conversation.base import Message

class Model(BaseModel):
    id: str


class Request(BaseModel):
    model: Model
    messages: list[Message]
    max_tokens: int | None = None
    stream: bool | None = None
