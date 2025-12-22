from abc import ABC, abstractmethod
from cv2.typing import MatLike

from shared.domain.aggregate.image import Image

from shared.application.tool.worker_pool import WorkerPool
from shared.application.tool.image_similarity import ImageSimilarity

from shared.infrastructure.dto.vo.data import Cv2ImageBinary

class HashSimilarity(ImageSimilarity, ABC):
    def __init__(self, worker_pool: WorkerPool, /) -> None:
        self._worker_pool = worker_pool

    async def similar(
        self,
        image1: Image,
        image2: Image,
        /,
        tolerance: float
    ) -> bool:
        return await self._worker_pool.run(
            self._do_similar,
            image1,
            image2,
            tolerance=tolerance
        )

    def _do_similar(
        self,
        image1: Image,
        image2: Image,
        /,
        tolerance: float
    ) -> bool:
        h1 = self._get_image_hash(image1)
        h2 = self._get_image_hash(image2)

        distance = self._hamming_distance(h1, h2)
        threshold = self._distance_threshold(tolerance)

        return distance <= threshold

    def _extract_frame(self, image: Image, /) -> MatLike:
        if isinstance(image.data, Cv2ImageBinary):
            return image.data.frame()

        raise TypeError("Unsupported image data type for frame extraction.")

    @abstractmethod
    def _get_image_hash(self, image: Image, /) -> int: ...

    @abstractmethod
    def _hamming_distance(self, h1: int, h2: int, /) -> float: ...

    @abstractmethod
    def _distance_threshold(self, tolerance: float) -> float: ...
