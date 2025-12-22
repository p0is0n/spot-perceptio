import cv2
import numpy as np

from shared.domain.aggregate.image import Image
from shared.infrastructure.tool.image_similarity.hash_similarity import HashSimilarity

class DHashSimilarity(HashSimilarity):
    _hash_size: int = 16
    _min: float = 0.02
    _max: float = 0.15

    def _get_image_hash(self, image: Image, /) -> int:
        frame = self._extract_frame(image)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, (self._hash_size + 1, self._hash_size))

        diff = (frame[:, 1:] > frame[:, :-1]).astype(np.uint8)

        packed = np.packbits(diff.reshape(-1))
        hash_value = int.from_bytes(packed.tobytes(), "big", signed=False)

        return hash_value

    def _hamming_distance(self, h1: int, h2: int, /) -> float:
        return ((h1 ^ h2).bit_count()) / (self._hash_size * self._hash_size)

    def _distance_threshold(self, tolerance: float) -> float:
        t: float = tolerance ** 0.38

        return self._min + t * (self._max - self._min)
