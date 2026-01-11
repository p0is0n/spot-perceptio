import argparse
import sys
import asyncio

from typing import Self
from dataclasses import dataclass
from pathlib import Path

from cv2.typing import MatLike
import cv2

from rich.console import Console
from rich.text import Text

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

# pylint: disable=wrong-import-position
from shared.domain.vo.coordinate import Coordinate, BoundingBox, Polygon
from shared.domain.aggregate.image import Image as SharedImage

from shared.infrastructure.tool.noop_worker_pool import NoopWorkerPool
from shared.infrastructure.log.noop_logger import NoopLogger
from shared.infrastructure.dto.vo.data import Cv2ImageBinary
from shared.infrastructure.tool.image_similarity.image_similarity import ImageSimilarityEvaluator
from shared.infrastructure.tool.image_similarity.dhash_similarity import DHashSimilarity
from shared.infrastructure.tool.image_similarity.phash_similarity import PHashSimilarity

IMAGES_DIR = Path("./tests/models/images/parking_spot")
IMAGES_RESULTS_DIR = Path("./tests/models/images/parking_spot/results")

IMAGES_EXTENSIONS = (".jpg", ".jpeg", ".png")

LABELS_FILE = Path("./tests/models/labels_data_compare.txt")

PARKING_SPOTS = {
    "A": [
        {
            "x": 1054,
            "y": 1423
        },
        {
            "x": 2511,
            "y": 1423
        },
        {
            "x": 2012,
            "y": 213
        },
        {
            "x": 1243,
            "y": 228
        }
    ],
    "B": [
        {
            "x": 387,
            "y": 230
        },
        {
            "x": 43,
            "y": 1408
        },
        {
            "x": 1064,
            "y": 1427
        },
        {
            "x": 1212,
            "y": 283
        }
    ]
}

@dataclass(frozen=True, slots=True)
class ParkingSpot:
    id: str
    coordinate: Polygon


@dataclass(frozen=True, slots=True)
class Image:
    id: str
    path: Path
    frame: MatLike

    @classmethod
    def load(cls, path: Path) -> Self:
        frame = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if frame is None:
            raise RuntimeError(f"Cannot read image {path}")

        image_id = cls._parse_filename(path.stem)
        return cls(
            image_id,
            path,
            frame
        )

    @staticmethod
    def _parse_filename(stem: str) -> str:
        return stem


@dataclass(slots=True)
class SimpleStats:
    total: int = 0
    match: int = 0

    def add(self, correct: bool) -> None:
        self.total += 1
        if correct:
            self.match += 1

    @property
    def mismatch(self) -> int:
        return self.total - self.match

    @property
    def accuracy(self) -> float:
        return (self.match / self.total) if self.total else 0.0


@dataclass(slots=True)
class SimplePerfStats:
    times: list[float]

    def add(self, t: float) -> None:
        self.times.append(t)

    @property
    def total(self) -> float:
        return sum(self.times)

    @property
    def avg(self) -> float:
        return self.total / len(self.times) if self.times else 0.0

    @property
    def min(self) -> float:
        return min(self.times) if self.times else 0.0

    @property
    def max(self) -> float:
        return max(self.times) if self.times else 0.0


def create_console(no_color: bool) -> Console:
    return Console(color_system=None if no_color else "auto")


def make_shared_image(image: Image) -> SharedImage:
    worker_pool = NoopWorkerPool()
    data = Cv2ImageBinary(image=image.frame, worker_pool=worker_pool)

    h, w = image.frame.shape[:2]
    coordinate = BoundingBox(
        p1=Coordinate(x=0, y=0),
        p2=Coordinate(x=w, y=h)
    )

    im = SharedImage(data=data, coordinate=coordinate)

    return im


async def compare_images(
    image1: Image,
    image2: Image,
    spot: ParkingSpot,
    *,
    tolerance: float = 0.3
) -> bool:
    worker_pool = NoopWorkerPool()
    logger = NoopLogger()

    im1 = await make_shared_image(image1).crop(spot.coordinate)
    im2 = await make_shared_image(image2).crop(spot.coordinate)

    dc = DHashSimilarity(worker_pool, logger)
    pc = PHashSimilarity(worker_pool, logger)

    ic = ImageSimilarityEvaluator(
        (dc, pc),
        logger
    )

    return await ic.similar(im1, im2, tolerance=tolerance)


def load_labeled_data(path: Path) -> list[tuple[tuple[str, ...], dict[str, bool | None]]]:
    pairs: list[tuple[tuple[str, ...], dict[str, bool | None]]] = []
    for line_no, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        try:
            files_part, *rest = line.split(",")
            images = files_part.split("|")

            decisions: dict[str, bool | None] = {}
            for item in rest:
                point, value = item.split("|")
                if value == "same":
                    decisions[point] = True
                elif value == "diff":
                    decisions[point] = False
                elif value == "-":
                    decisions[point] = None
                else:
                    raise ValueError(f"Invalid value '{value}'")

            pairs.append((tuple(images), decisions))
        except Exception as exc:
            raise ValueError(
                f"Invalid data format at line {line_no}: {raw}"
            ) from exc

    return pairs


async def run_test(
    results: bool,
    console: Console,
    /
) -> None:
    console.print("[b]Load labels:[/b]", f"[b]{LABELS_FILE}[/b]")

    labels_data = load_labeled_data(LABELS_FILE)
    if not labels_data:
        raise RuntimeError("No test labels found.")

    spots: tuple[ParkingSpot, ...] = tuple(
        ParkingSpot(
            id=sid,
            coordinate=Polygon(
                corners=[Coordinate(x=p['x'], y=p['y']) for p in corners]
            )
        )
        for sid, corners in PARKING_SPOTS.items()
    )

    matched_stats = SimpleStats()
    for images, decisions in labels_data:
        if len(images) != 2:
            raise ValueError(f"Invalid number of images: {len(images)}")

        for spot in spots:
            image1, image2 = map(lambda image: Image.load(IMAGES_DIR.joinpath(image)), images)

            decision = decisions[spot.id]
            similared = await compare_images(image1, image2, spot)

            matched = similared == decision
            matched_stats.add(matched)

            if matched:
                continue

            status_text = Text("YES" if similared else "NO")
            status_text.stylize("bold")
            status_text.stylize(
                "green" if matched else "red"
            )

            console.print(
                "[b]Similar:[/b]",
                f"[cyan]{spot.id}[/cyan]",
                f"[yellow]{image1.id}[/yellow] / [yellow]{image2.id}[/yellow]",
                status_text
            )

    console.print()
    console.print(f"Total checks: {matched_stats.total}")
    console.print(f"Matches (M): {matched_stats.match}")
    console.print(f"Mismatches (M): {matched_stats.mismatch}")
    console.print(f"Accuracy (M): {matched_stats.accuracy*100:.1f}%")


if __name__ == "__main__":
    if not IMAGES_DIR.exists():
        raise RuntimeError(f"Images directory not found: {IMAGES_DIR}")

    parser = argparse.ArgumentParser(description="Parking Spot test")
    parser.add_argument("--with-results", action="store_true", help="Create result images")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    output_console = create_console(args.no_color)
    asyncio.run(
        run_test(
            args.with_results,
            output_console,
        )
    )
