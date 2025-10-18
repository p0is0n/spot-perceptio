from pydantic import BaseModel

from shared.application.service.llm.dto.conversation.base import Message

class Choice(BaseModel):
    index: float
    message: Message


class Response(BaseModel):
    id: str | None = None
    choices: list[Choice]
