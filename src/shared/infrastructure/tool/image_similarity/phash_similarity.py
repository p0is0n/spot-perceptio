import cv2
import numpy as np

from shared.domain.aggregate.image import Image
from shared.infrastructure.tool.image_similarity.hash_similarity import HashSimilarity

class PHashSimilarity(HashSimilarity):
    _hash_size: int = 32
    _lowfreq_size: int = 6
    _min: float = 0.08
    _max: float = 0.40

    def _get_image_hash(self, image: Image, /) -> int:
        frame = self._extract_frame(image)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (self._hash_size, self._hash_size))

        dct = cv2.dct(resized.astype(np.float32))
        norm = np.linalg.norm(dct)
        if norm > 0:
            dct = dct / norm

        low = dct[: self._lowfreq_size, : self._lowfreq_size]

        flat = low.flatten()
        rest = flat[1:]

        median = float(np.median(rest.astype(np.float32, copy=False)))
        bits = rest > median

        packed = np.packbits(bits.astype(np.uint8))
        hash_value = int.from_bytes(packed.tobytes(), "big", signed=False)

        return hash_value

    def _hamming_distance(self, h1: int, h2: int, /) -> float:
        return (h1 ^ h2).bit_count() / ((self._lowfreq_size * self._lowfreq_size) - 1)

    def _distance_threshold(self, tolerance: float) -> float:
        return self._min + tolerance * (self._max - self._min)
