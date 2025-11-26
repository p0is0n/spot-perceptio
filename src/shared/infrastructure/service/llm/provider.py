from openai import AsyncOpenAI as OpenAI

from shared.application.service.llm.provider import LLMProvider
from shared.application.service.llm.dto import conversation

class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = OpenAI()

    async def conversation(
        self,
        request: conversation.Request,
        /
    ) -> conversation.Response:
        raise NotImplementedError
