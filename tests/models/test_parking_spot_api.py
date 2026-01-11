import argparse
import sys
import base64
import time
import math
import asyncio

from typing import Any, Self
from dataclasses import dataclass
from pathlib import Path

from cv2.typing import MatLike

import httpx
import cv2
import numpy as np

from rich.console import Console
from rich.text import Text

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

# pylint: disable=wrong-import-position
from shared.domain.vo.coordinate import Coordinate, Polygon

API_URL = "http://127.0.0.1:8001/parking/analyze_spots"
API_MAX_CONCURRENCY = 10

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

COLOR_WHITE = (230, 230, 230)
COLOR_GREEN = (0, 255, 0)
COLOR_GRAY = (160, 160, 160)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_BLUE = (255, 0, 0)

@dataclass(frozen=True, slots=True)
class ParkingSpot:
    id: str
    coordinate: Polygon


@dataclass(frozen=True, slots=True)
class SpotStatusCoordinate:
    coordinate: Polygon
    label: str | None


@dataclass(frozen=True, slots=True)
class SpotStatus:
    spot_id: str
    occupied: bool
    vehicle_coordinate: SpotStatusCoordinate | None = None
    plate_coordinate: SpotStatusCoordinate | None = None

    @classmethod
    def from_digit(cls, spot_id: str, digit: str) -> Self:
        if digit == "1":
            return cls(spot_id, True)

        if digit == "0":
            return cls(spot_id, False)

        raise ValueError(f"Invalid status digit: {digit}")

    @property
    def is_identified(self) -> bool:
        return (
            self.occupied
            and self.vehicle_coordinate is not None
            and self.plate_coordinate is not None
        )


@dataclass(frozen=True, slots=True)
class Image:
    id: str
    path: Path
    expected_spots_status: tuple[SpotStatus, ...]
    frame: MatLike
    data: str

    @classmethod
    def load(cls, path: Path) -> Self:
        frame = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if frame is None:
            raise RuntimeError(f"Cannot read image {path}")

        image_id, expected_spots_status = cls._parse_filename(path.stem)
        data = cls._encode_to_data(frame)

        return cls(
            image_id,
            path,
            expected_spots_status,
            frame,
            data
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

    @staticmethod
    def _encode_to_data(frame: MatLike) -> str:
        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            raise RuntimeError("Failed to encode image")

        return base64.b64encode(buf.tobytes()).decode("utf-8")


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
    
    def percentile(self, p: float) -> float:
        if not self.times:
            return 0.0

        if not 0 <= p <= 100:
            raise ValueError("Percentile must be in range [0, 100]")

        values = sorted(self.times)
        k = (len(values) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)

        if f == c:
            return values[int(k)]

        return values[f] + (values[c] - values[f]) * (k - f)

    @property
    def p50(self) -> float:
        return self.percentile(50)

    @property
    def p95(self) -> float:
        return self.percentile(95)

    @property
    def p99(self) -> float:
        return self.percentile(99)


@dataclass(frozen=True, slots=True)
class TaskResult:
    image: Image
    spot: ParkingSpot
    actual: SpotStatus
    elapsed: float


@dataclass(frozen=True, slots=True)
class TasksResult:
    image: Image
    spots: tuple[ParkingSpot, ...]
    actual: tuple[SpotStatus, ...]
    elapsed: float


def create_console(no_color: bool) -> Console:
    return Console(color_system=None if no_color else "auto")


async def detect_vehicle_in_spot(
    client: httpx.AsyncClient,
    image: Image,
    spot: ParkingSpot,
    /
) -> SpotStatus:
    payload = {
        "image": {"data": image.data},
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
        response = await client.put(
            API_URL,
            json=payload,
            timeout=5.0,
        )
    except Exception as exc:
        raise RuntimeError(f"HTTPX request error: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"API error {response.status_code}: {response.text}"
        )

    occupied = False
    vehicle_coordinate: SpotStatusCoordinate | None = None
    plate_coordinate: SpotStatusCoordinate | None = None

    data = response.json()
    try:
        occupied = data["data"]["parking_spot"]["occupied"]
        if occupied:
            vehicle = data["data"]["parking_spot"]["vehicle"]
            vehicle_coordinate = SpotStatusCoordinate(
                coordinate=Polygon(
                    corners=tuple(
                        Coordinate(
                            x=c["x"],
                            y=c["y"]
                        )
                        for c in vehicle["coordinate"]["corners"]
                    )
                ),
                label=None
            )

            if vehicle["plate"] is not None:
                plate_coordinate = SpotStatusCoordinate(
                    coordinate=Polygon(
                        corners=tuple(
                            Coordinate(
                                x=c["x"],
                                y=c["y"]
                            )
                            for c in vehicle["plate"]["coordinate"]["corners"]
                        )
                    ),
                    label=vehicle["plate"]["value"]
                )
    except Exception as exc:
        raise RuntimeError(
            f"Invalid response schema: {exc}\nResponse: {data}"
        ) from exc

    return SpotStatus(
        spot.id,
        occupied,
        vehicle_coordinate,
        plate_coordinate
    )


async def detect_vehicle_in_spots(
    client: httpx.AsyncClient,
    image: Image,
    spots: tuple[ParkingSpot, ...],
    /
) -> tuple[SpotStatus, ...]:
    payload = {
        "image": {"data": image.data},
        "spots": [{
            "id": spot.id,
            "coordinate": {
                "corners": [
                    {"x": c.x, "y": c.y}
                    for c in spot.coordinate.corners
                ]
            }
        } for spot in spots]
    }

    try:
        response = await client.put(
            API_URL,
            json=payload,
            timeout=5.0,
        )
    except Exception as exc:
        raise RuntimeError(f"HTTPX request error: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"API error {response.status_code}: {response.text}"
        )

    spots_status: list[SpotStatus] = []
    data = response.json()
    try:
        for parking_spot in data["data"]["parking_spots"]:
            vehicle_coordinate: SpotStatusCoordinate | None = None
            plate_coordinate: SpotStatusCoordinate | None = None

            occupied = parking_spot["occupied"]
            if occupied:
                vehicle = parking_spot["vehicle"]
                vehicle_coordinate = SpotStatusCoordinate(
                    coordinate=Polygon(
                        corners=tuple(
                            Coordinate(
                                x=c["x"],
                                y=c["y"]
                            )
                            for c in vehicle["coordinate"]["corners"]
                        )
                    ),
                    label=None
                )

                if vehicle["plate"] is not None:
                    plate_coordinate = SpotStatusCoordinate(
                        coordinate=Polygon(
                            corners=tuple(
                                Coordinate(
                                    x=c["x"],
                                    y=c["y"]
                                )
                                for c in vehicle["plate"]["coordinate"]["corners"]
                            )
                        ),
                        label=vehicle["plate"]["value"]
                    )

            spots_status.append(SpotStatus(
                parking_spot["spot"]["id"],
                occupied,
                vehicle_coordinate,
                plate_coordinate
            ))
    except Exception as exc:
        raise RuntimeError(
            f"Invalid response schema: {exc}\nResponse: {data}"
        ) from exc

    return tuple(spots_status)


async def detect_vehicle_in_spot_task(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    image: Image,
    spot: ParkingSpot,
    /
) -> TaskResult:
    async with semaphore:
        start = time.perf_counter()
        try:
            result = await detect_vehicle_in_spot(
                client,
                image,
                spot
            )
        finally:
            elapsed = time.perf_counter() - start

        return TaskResult(
            image,
            spot,
            result,
            elapsed
        )


async def detect_vehicle_in_spots_task(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    image: Image,
    spots: tuple[ParkingSpot, ...],
    /
) -> TasksResult:
    async with semaphore:
        start = time.perf_counter()
        try:
            result = await detect_vehicle_in_spots(
                client,
                image,
                spots
            )
        finally:
            elapsed = time.perf_counter() - start

        return TasksResult(
            image,
            spots,
            result,
            elapsed
        )


def draw_detection_on_image(
    image: Image,
    spot: ParkingSpot,
    spot_status: SpotStatus,
    spot_match: bool,
    output_path: Path
) -> None:
    img = image.frame.copy()
    coordinates: list[tuple[SpotStatusCoordinate, Any]] = []
    if spot_status.vehicle_coordinate is not None:
        coordinates.append((spot_status.vehicle_coordinate, COLOR_GREEN))

    if spot_status.plate_coordinate is not None:
        coordinates.append((spot_status.plate_coordinate, COLOR_GREEN))

    for coordinate, box_color in coordinates:
        poly_pts = coordinate_to_polygon(coordinate.coordinate)
        cv2.polylines(
            img,
            [poly_pts],
            isClosed=True,
            color=box_color,
            thickness=4
        )

        if coordinate.label is not None:
            cv2.putText(img, coordinate.label,
                (int(coordinate.coordinate.x1) - 10, int(coordinate.coordinate.y1) - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                COLOR_WHITE, 2)

    poly_pts = coordinate_to_polygon(spot.coordinate)
    cv2.polylines(
        img,
        [poly_pts],
        isClosed=True,
        color=COLOR_BLUE,
        thickness=2
    )

    cv2.circle(img, (20, 20), 10, COLOR_GREEN if spot_match else COLOR_ORANGE, -1)
    cv2.imwrite(str(output_path), img)


def coordinate_to_polygon(
    coordinate: Polygon
) -> np.typing.NDArray[np.float32]:
    return np.array(coordinate.to_tuple_list(), dtype=np.int32)


def get_expected_status_for_spot(image: Image, spot_id: str) -> SpotStatus | None:
    for s in image.expected_spots_status:
        if s.spot_id == spot_id:
            return s

    return None


async def run_test(
    results: bool,
    console: Console,
    /
) -> None:
    console.print("[b]Search images:[/b]", f"[b]{IMAGES_DIR}[/b]")

    images_strict: list[str] = [
        # "8759_A1_B0",
        # "8758_A0_B1",
    ]
    images: list[Image] = [
        Image.load(p) for p in sorted([
            p for p in IMAGES_DIR.iterdir()
            if p.suffix.lower() in IMAGES_EXTENSIONS and "_" in p.stem
                and (not images_strict or p.stem in images_strict)
        ])
    ]

    if not images:
        raise RuntimeError("No test images found.")
    console.print("[b]Images:[/b]", f"[b]{len(images)}[/b]")

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
    identified_stats = SimpleStats()
    perf_stats = SimplePerfStats(times=[])

    semaphore = asyncio.Semaphore(API_MAX_CONCURRENCY)
    tasks = []

    async with httpx.AsyncClient() as client:
        for image in images:
            tasks.append(detect_vehicle_in_spots_task(
                semaphore,
                client,
                image,
                spots
            ))

        wall_start = time.perf_counter()
        tasks_results: list[TasksResult] = await asyncio.gather(*tasks)
        wall_elapsed = time.perf_counter() - wall_start

        for result in tasks_results:
            console.print()
            console.print(f"[b]Image:[/b] [yellow]{result.image.id}[/yellow]")

            for spot in spots:
                expected = get_expected_status_for_spot(result.image, spot.id)
                actual = next(actual for actual in result.actual if actual.spot_id == spot.id)
                if expected is None:
                    raise RuntimeError(
                        f"Expected status for spot {spot.id} not found "
                        f"in image {result.image.id}"
                    )

                matched = expected.occupied == actual.occupied
                identified = (
                    not expected.occupied
                    or (
                        expected.occupied
                        and actual.is_identified
                    )
                )

                matched_stats.add(matched)
                identified_stats.add(identified)
                perf_stats.add(result.elapsed)

                if results:
                    output_file = IMAGES_RESULTS_DIR / f"{result.image.id}_{spot.id}_result.jpg"
                    draw_detection_on_image(
                        result.image,
                        spot,
                        actual,
                        matched,
                        output_file
                    )

                status_text = Text("OCCUPIED" if actual.occupied else "FREE")
                status_text.stylize("bold")
                status_text.stylize(
                    "green" if matched else "red"
                )

                console.print(
                    "[b]Spot:[/b]",
                    f"[cyan]{spot.id}[/cyan]",
                    f"{result.elapsed*1000:.1f} ms",
                    status_text
                )

    effective_concurrency = perf_stats.total / wall_elapsed if wall_elapsed else 0.0

    console.print()
    console.print(f"Total checks: {matched_stats.total}")
    console.print(f"Matches (M): {matched_stats.match}")
    console.print(f"Mismatches (M): {matched_stats.mismatch}")
    console.print(f"Accuracy (M): {matched_stats.accuracy*100:.1f}%")
    console.print(f"Matches (I): {identified_stats.match}")
    console.print(f"Mismatches (I): {identified_stats.mismatch}")
    console.print(f"Accuracy (I): {identified_stats.accuracy*100:.1f}%")
    console.print()
    console.print(f"Wall time: {wall_elapsed:.3f} s")
    console.print(f"Sum of request times: {perf_stats.total:.3f} s")
    console.print(f"Effective concurrency: {effective_concurrency:.2f}x")
    console.print(f"Avg per call: {perf_stats.avg*1000:.1f} ms")
    console.print(f"Min: {perf_stats.min*1000:.1f} ms")
    console.print(f"Max: {perf_stats.max*1000:.1f} ms")
    console.print(f"p50: {perf_stats.p50*1000:.1f} ms")
    console.print(f"p95: {perf_stats.p95*1000:.1f} ms")
    console.print(f"p99: {perf_stats.p99*1000:.1f} ms")

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
