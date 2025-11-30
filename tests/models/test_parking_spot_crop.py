import argparse

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

MODELS_DIR = Path("./models/ul")

IMAGES_DIR = Path("./tests/models/images/parking_spot")
IMAGES_EXTENSIONS = (".jpg", ".jpeg", ".png")

PARKING_SPOTS = {
    "A": [
        {
            "x": 1251,
            "y": 13
        },
        {
            "x": 1180,
            "y": 511
        },
        {
            "x": 1118,
            "y": 923
        },
        {
            "x": 1060,
            "y": 1428
        },
        {
            "x": 1877,
            "y": 1422
        },
        {
            "x": 2502,
            "y": 1412
        },
        {
            "x": 2431,
            "y": 1195
        },
        {
            "x": 2048,
            "y": 107
        },
        {
            "x": 1907,
            "y": 20
        },
        {
            "x": 1586,
            "y": 5
        }
    ],
    "B": [
        {
            "x": 384,
            "y": 152
        },
        {
            "x": 154,
            "y": 615
        },
        {
            "x": 15,
            "y": 978
        },
        {
            "x": 43,
            "y": 1408
        },
        {
            "x": 504,
            "y": 1419
        },
        {
            "x": 1064,
            "y": 1427
        },
        {
            "x": 1153,
            "y": 699
        },
        {
            "x": 1249,
            "y": 26
        },
        {
            "x": 923,
            "y": 0
        },
        {
            "x": 791,
            "y": 9
        },
        {
            "x": 573,
            "y": 222
        }
    ]
}

VEHICLE_IDS = {1, 2, 3, 5, 7}


@dataclass(frozen=True, slots=True)
class Corner:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class ParkingSpot:
    id: str
    corners: list[Corner]

    def as_polygon(self) -> np.typing.NDArray[np.float32]:
        return np.array([(c.x, c.y) for c in self.corners], dtype=np.int32)


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


def create_console(no_color: bool) -> Console:
    return Console(color_system=None if no_color else "auto")


def detect_vehicle_in_spot(
    model: Model,
    image: Image,
    spot: ParkingSpot,
    threshold: float,
    /
) -> SpotStatus:
    mask = np.zeros(image.frame.shape[:2], dtype=np.uint8)
    pts = spot.as_polygon()

    cv2.fillPoly(mask, [pts], 255)

    masked = cv2.bitwise_and(image.frame, image.frame, mask=mask)
    x, y, w, h = cv2.boundingRect(pts)

    cropped = masked[y:y+h, x:x+w].copy()
    results = model.predict(cropped, verbose=False)[0]

    detections = []
    for box in results.boxes: # type: ignore
        cls = int(box.cls)
        if cls not in VEHICLE_IDS:
            continue

        if box.conf < threshold:
            continue

        xyxy = box.xyxy[0].tolist()

        gx1 = xyxy[0] + x
        gy1 = xyxy[1] + y
        gx2 = xyxy[2] + x
        gy2 = xyxy[3] + y

        detections.append(((gx1, gy1, gx2, gy2), cls, float(box.conf)))

    occupied = len(detections) > 0

    return SpotStatus(spot.id, occupied)


def get_expected_status_for_spot(image: Image, spot_id: str) -> SpotStatus | None:
    for s in image.expected_spots_status:
        if s.spot_id == spot_id:
            return s

    return None


def run_test(model_filename: str, threshold: float, console: Console, /) -> None:
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
            corners=[Corner(**p) for p in corners]
        )
        for sid, corners in PARKING_SPOTS.items()
    )

    overall_stats = SimpleStats()
    for image_path in images:
        image = Image.load(image_path)

        console.print()
        console.print(f"[b]Image:[/b] [yellow]{image.id}[/yellow]")

        for spot in spots:
            actual = detect_vehicle_in_spot(model, image, spot, threshold)
            expected = get_expected_status_for_spot(image, spot.id)
            if expected is None:
                raise RuntimeError(
                    f"Expected status for spot {spot.id} not found "
                    f"in image {image.id}"
                )

            overall_stats.add(expected.occupied == actual.occupied)

            status_text = Text("OCCUPIED" if actual.occupied else "FREE")
            status_text.stylize("bold")
            status_text.stylize(
                "green" if expected.occupied == actual.occupied else "red"
            )

            console.print("[b]Spot:[/b]", f"[cyan]{spot.id}[/cyan]", status_text)

    console.print()
    console.print(f"Total checks: {overall_stats.total}")
    console.print(f"Matches: {overall_stats.match}")
    console.print(f"Mismatches: {overall_stats.mismatch}")
    console.print(f"Accuracy: {overall_stats.accuracy*100:.1f}%")

if __name__ == "__main__":
    if not MODELS_DIR.exists():
        raise RuntimeError(f"Models directory not found: {MODELS_DIR}")

    if not IMAGES_DIR.exists():
        raise RuntimeError(f"Images directory not found: {IMAGES_DIR}")

    parser = argparse.ArgumentParser(description="Parking Spot test")
    parser.add_argument("--model", required=True, help="YOLO model filename")
    parser.add_argument("--threshold", type=float, default=0.6, help="Detection threshold")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    output_console = create_console(args.no_color)
    run_test(args.model, args.threshold, output_console)
