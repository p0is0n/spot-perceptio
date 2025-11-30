import argparse
import sys
import time

from typing import Self
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from cv2.typing import MatLike

from ultralytics.engine.model import Model
from ultralytics import YOLO # type: ignore[attr-defined]

from rich.console import Console
from rich.text import Text

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

# pylint: disable=wrong-import-position
from shared.domain.vo.coordinate import Coordinate, BoundingBox, RotatedBoundingBox, Polygon

MODELS_DIR = Path("./models/ul")

IMAGES_DIR = Path("./tests/models/images/parking_spot")
IMAGES_RESULTS_DIR = Path("./tests/models/images/parking_spot/results")

IMAGES_EXTENSIONS = (".jpg", ".jpeg", ".png")

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

VEHICLE_IDS = {1, 2, 3, 5, 7}

COLOR_GREEN = (0, 255, 0)
COLOR_GRAY = (160, 160, 160)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_BLUE = (255, 0, 0)

@dataclass(frozen=True, slots=True)
class Corner:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class ParkingSpot:
    id: str
    coordinate: Polygon


@dataclass(frozen=True, slots=True)
class SpotStatus:
    spot_id: str
    occupied: bool

    @classmethod
    def from_digit(cls, spot_id: str, digit: str) -> Self:
        if digit == "1":
            return cls(spot_id, True)

        if digit == "0":
            return cls(spot_id, False)

        raise ValueError(f"Invalid status digit: {digit}")


@dataclass(frozen=True, slots=True)
class Image:
    id: str
    path: Path
    expected_spots_status: tuple[SpotStatus, ...]
    frame: MatLike

    @classmethod
    def load(cls, path: Path) -> Self:
        frame = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if frame is None:
            raise RuntimeError(f"Cannot read image {path}")

        image_id, expected_spots_status = cls._parse_filename(path.stem)
        return cls(
            image_id,
            path,
            expected_spots_status,
            frame
        )

    @staticmethod
    def _parse_filename(stem: str) -> tuple[str, tuple[SpotStatus, ...]]:
        image_id = stem
        parts = stem.split("_")
        if len(parts) < 2:
            raise ValueError(f"Invalid image filename format: {stem}")

        spot_parts = parts[1:]
        result: list[SpotStatus] = []

        for sp in spot_parts:
            if len(sp) < 2:
                raise ValueError(f"Invalid spot status format: {sp}")

            spot_id = sp[0]
            status_digit = sp[1]

            result.append(SpotStatus.from_digit(spot_id, status_digit))

        expected_count = len(PARKING_SPOTS)
        if len(result) != expected_count:
            raise ValueError(
                f"Expected {expected_count} spot statuses, got {len(result)} "
                f"for image '{stem}'"
            )

        return image_id, tuple(result)


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


def detect_vehicle_in_spot(
    model: Model,
    image: Image,
    spot: ParkingSpot,
    threshold: float,
    /
) -> tuple[SpotStatus, list[tuple[
        BoundingBox | RotatedBoundingBox,
        int,
        float
    ]]]:
    results = model.predict(image.frame, verbose=False)[0]
    detections: list[tuple[
        BoundingBox | RotatedBoundingBox,
        int,
        float
    ]] = []

    for box in results.boxes: # type: ignore
        cls = int(box.cls)
        if cls not in VEHICLE_IDS:
            continue

        if box.conf < threshold:
            continue

        xyxy = box.xyxy.cpu().numpy()[0]
        coordinate = to_bounding_box_coordinate(xyxy)

        detections.append((
            coordinate,
            cls,
            float(box.conf)
        ))

    occupied = False
    for box, cls, _ in detections:
        if box_in_coordinate(box, spot.coordinate):
            occupied = True
            break

    return SpotStatus(spot.id, occupied), detections



def draw_detection_on_image(
    image: Image,
    detections: list[tuple[
        BoundingBox | RotatedBoundingBox,
        int,
        float
    ]],
    spot: ParkingSpot,
    spot_match: bool,
    output_path: Path
) -> None:
    img = image.frame.copy()
    spot_color = COLOR_YELLOW if spot_match else COLOR_ORANGE

    pts = coordinate_to_polygon(spot.coordinate)
    cv2.polylines(img, [pts], True, spot_color, 3)

    for coordinate, cls_id, conf in detections:
        cx = (coordinate.x1 + coordinate.x2) / 2
        cy = (coordinate.y1 + coordinate.y2) / 2

        inside = cv2.pointPolygonTest(pts, (cx, cy), False) >= 0
        box_color = COLOR_GREEN if inside else COLOR_GRAY

        cv2.rectangle(img,
                      (int(coordinate.x1), int(coordinate.y1)),
                      (int(coordinate.x2), int(coordinate.y2)),
                      box_color, 4)

        cv2.circle(img, (int(cx), int(cy)), 10, COLOR_BLUE, -1)

        text = f"{cls_id}:{conf:.2f}"
        cv2.putText(img, text, (int(coordinate.x1) + 10, int(coordinate.y1) + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    box_color, 2)

    cv2.imwrite(str(output_path), img)


def to_bounding_box_coordinate(
    xyxy: np.typing.NDArray[np.float32]
) -> BoundingBox:
    x1, y1, x2, y2 = map(int, xyxy.tolist())

    return BoundingBox(
        p1=Coordinate(x=x1, y=y1),
        p2=Coordinate(x=x2, y=y2),
    )


def box_in_coordinate(
    box: BoundingBox | RotatedBoundingBox,
    coordinate: BoundingBox | RotatedBoundingBox | Polygon,
    /
) -> bool:
    polygon = coordinate_to_polygon(coordinate)
    if isinstance(box, BoundingBox):
        cx = (box.x1 + box.x2) / 2
        cy = (box.y1 + box.y2) / 2
    elif isinstance(box, RotatedBoundingBox):
        cx = box.width / 2
        cy = box.height / 2
    else:
        raise NotImplementedError("Unsupported box coordinate type.")

    return cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0


def coordinate_to_polygon(
    coordinate: BoundingBox | RotatedBoundingBox | Polygon
) -> np.typing.NDArray[np.float32]:
    if isinstance(coordinate, Polygon):
        return np.array(coordinate.to_tuple_list(), dtype=np.int32)

    raise NotImplementedError("Unsupported coordinate type.")

def get_expected_status_for_spot(image: Image, spot_id: str) -> SpotStatus | None:
    for s in image.expected_spots_status:
        if s.spot_id == spot_id:
            return s

    return None


def run_test(
    model_filename: str,
    threshold: float,
    results: bool,
    console: Console,
    /
) -> None:
    console.print("[b]Loading model:[/b]", f"[b]{model_filename}[/b]")
    model = YOLO(MODELS_DIR.joinpath(model_filename))

    console.print("[b]Search images:[/b]", f"[b]{IMAGES_DIR}[/b]")
    images = sorted(
        [p for p in IMAGES_DIR.iterdir()
        if p.suffix.lower() in IMAGES_EXTENSIONS and "_" in p.stem]
    )
    if not images:
        raise RuntimeError("No test images found.")

    spots: tuple[ParkingSpot, ...] = tuple(
        ParkingSpot(
            id=sid,
            coordinate=Polygon(
                corners=[Coordinate(x=p['x'], y=p['y']) for p in corners]
            )
        )
        for sid, corners in PARKING_SPOTS.items()
    )

    overall_stats = SimpleStats()
    perf_stats = SimplePerfStats(times=[])

    for image_path in images:
        image = Image.load(image_path)

        console.print()
        console.print(f"[b]Image:[/b] [yellow]{image.id}[/yellow]")

        for spot in spots:
            start = time.perf_counter()
            actual, detections = detect_vehicle_in_spot(model, image, spot, threshold)
            elapsed = time.perf_counter() - start

            perf_stats.add(elapsed)
            console.print(f"{elapsed*1000:.1f} ms", style="dim")

            expected = get_expected_status_for_spot(image, spot.id)
            if expected is None:
                raise RuntimeError(
                    f"Expected status for spot {spot.id} not found "
                    f"in image {image.id}"
                )

            matched = expected.occupied == actual.occupied
            if results:
                output_file = IMAGES_RESULTS_DIR / f"{image.id}_{spot.id}_result.jpg"
                draw_detection_on_image(
                    image,
                    detections,
                    spot,
                    matched,
                    output_file
                )

            overall_stats.add(matched)

            status_text = Text("OCCUPIED" if actual.occupied else "FREE")
            status_text.stylize("bold")
            status_text.stylize(
                "green" if matched else "red"
            )

            console.print("[b]Spot:[/b]", f"[cyan]{spot.id}[/cyan]", status_text)

    console.print()
    console.print(f"Total checks: {overall_stats.total}")
    console.print(f"Matches: {overall_stats.match}")
    console.print(f"Mismatches: {overall_stats.mismatch}")
    console.print(f"Accuracy: {overall_stats.accuracy*100:.1f}%")
    console.print()
    console.print(f"Total time: {perf_stats.total:.3f} s")
    console.print(f"Avg per call: {perf_stats.avg*1000:.1f} ms")
    console.print(f"Min: {perf_stats.min*1000:.1f} ms")
    console.print(f"Max: {perf_stats.max*1000:.1f} ms")

if __name__ == "__main__":
    if not MODELS_DIR.exists():
        raise RuntimeError(f"Models directory not found: {MODELS_DIR}")

    if not IMAGES_DIR.exists():
        raise RuntimeError(f"Images directory not found: {IMAGES_DIR}")

    parser = argparse.ArgumentParser(description="Parking Spot test")
    parser.add_argument("--model", required=True, help="YOLO model filename")
    parser.add_argument("--threshold", type=float, default=0.6, help="Detection threshold")
    parser.add_argument("--with-results", action="store_true", help="Create result images")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    output_console = create_console(args.no_color)
    run_test(
        args.model,
        args.threshold,
        args.with_results,
        output_console
    )
