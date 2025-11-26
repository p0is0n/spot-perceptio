from typing import Protocol

from shared.application.service.ml.dto import detection

class MLDetectionProvider(Protocol):
    async def predict(self, request: detection.Request, /) -> detection.Response: ...
