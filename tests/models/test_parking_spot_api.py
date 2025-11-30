import argparse
import sys
import base64
import time

from typing import Self
from dataclasses import dataclass
from pathlib import Path

from cv2.typing import MatLike

import httpx
import cv2

from rich.console import Console
from rich.text import Text

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

# pylint: disable=wrong-import-position
from shared.domain.vo.coordinate import Coordinate, Polygon

API_URL = "http://127.0.0.1:8001/parking/analyze_spot"

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
    image: Image,
    spot: ParkingSpot,
    /
) -> SpotStatus:
    ok, buf = cv2.imencode(".jpg", image.frame)
    if not ok:
        raise RuntimeError("Failed to encode image")

    data = base64.b64encode(buf.tobytes()).decode("utf-8")
    payload = {
        "image": {"data": data},
        "spot": {
            "id": spot.id,
            "coordinate": {
                "corners": [
                    {"x": c.x, "y": c.y}
                    for c in spot.coordinate.corners
                ]
            }
        }
    }

    try:
        response = httpx.put(
            API_URL,
            json=payload,
            timeout=10.0,
        )
    except Exception as exc:
        raise RuntimeError(f"HTTPX request error: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"API error {response.status_code}: {response.text}"
        )

    data = response.json()
    try:
        occupied = data["data"]["parking_spot"]["occupied"]
    except Exception as exc:
        raise RuntimeError(
            f"Invalid response schema: {exc}\nResponse: {data}"
        ) from exc

    return SpotStatus(spot.id, occupied)


def get_expected_status_for_spot(image: Image, spot_id: str) -> SpotStatus | None:
    for s in image.expected_spots_status:
        if s.spot_id == spot_id:
            return s

    return None


def run_test(
    console: Console,
    /
) -> None:
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
            actual = detect_vehicle_in_spot(image, spot)
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
    if not IMAGES_DIR.exists():
        raise RuntimeError(f"Images directory not found: {IMAGES_DIR}")

    parser = argparse.ArgumentParser(description="Parking Spot test")
    parser.add_argument("--with-results", action="store_true", help="Create result images")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    args = parser.parse_args()

    output_console = create_console(args.no_color)
    run_test(
        output_console
    )
