from shared.domain.aggregate.image import Image

from shared.application.log import Logger
from shared.application.tool.image_similarity import ImageSimilarity

class ImageSimilarityEvaluator(ImageSimilarity):
    def __init__(
        self,
        strategies: tuple[ImageSimilarity, ...],
        logger: Logger
    ) -> None:
        if not strategies:
            raise ValueError("Requires at least one strategy")

        self._strategies = strategies
        self._logger = logger

        self._logger.debug(
            "Initialized",
            data={
                "strategies": len(self._strategies),
            },
            tags=("image_similarity_evaluator", "init"),
        )

    async def similar(
        self,
        image1: Image,
        image2: Image,
        /,
        tolerance: float
    ) -> bool:
        for strategy in self._strategies:
            if await strategy.similar(image1, image2, tolerance=tolerance):
                self._logger.debug(
                    "Similarity found",
                    data={
                        "image1": await image1.fingerprint(),
                        "image2": await image2.fingerprint(),
                        "tolerance": tolerance,
                        "strategy": strategy.__class__.__name__,
                    },
                    tags=("image_similarity_evaluator", "similar"),
                )

                return True

        self._logger.debug(
            "Not similar in any strategy",
            data={
                "image1": await image1.fingerprint(),
                "image2": await image2.fingerprint(),
                "tolerance": tolerance,
            },
            tags=("image_similarity_evaluator", "similar"),
        )

        return False
