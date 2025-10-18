from typing import Protocol

from shared.application.service.llm.dto import conversation

class LLMProvider(Protocol):
    async def conversation(
        self,
        request: conversation.Request
    ) -> conversation.Response: ...
