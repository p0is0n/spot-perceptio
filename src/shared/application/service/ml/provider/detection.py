from typing import Protocol

from shared.application.service.ml.dto import detection

class MlDetectionProvider(Protocol):
    async def predict(self, request: detection.Request, /) -> detection.Response: ...
