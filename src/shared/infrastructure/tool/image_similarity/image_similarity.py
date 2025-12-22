from shared.domain.aggregate.image import Image
from shared.application.tool.image_similarity import ImageSimilarity

class ImageSimilarityEvaluator(ImageSimilarity):
    def __init__(self, strategies: tuple[ImageSimilarity, ...]) -> None:
        if not strategies:
            raise ValueError("Requires at least one strategy")

        self._strategies = strategies

    async def similar(
        self,
        image1: Image,
        image2: Image,
        /,
        tolerance: float
    ) -> bool:
        for strategy in self._strategies:
            if await strategy.similar(image1, image2, tolerance=tolerance):
                return True

        return False
