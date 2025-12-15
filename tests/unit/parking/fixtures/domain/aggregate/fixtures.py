# pylint: disable=redefined-outer-name
from typing import Any

import pytest

from shared.domain.vo.base import Id
from shared.domain.aggregate.spot import Spot
from shared.domain.vo.coordinate import Polygon, Coordinate

from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails, VehicleObserved
from parking.domain.enum.vehicle import VehicleType
from parking.domain.enum.color import Color

def create_spots(count: int, prefix_id: str = "test-spot") -> Any:
    spots = []

    for i in range(count):
        spot_id = f"{prefix_id}-{i+1}"
        x1 = 10.0 + (i * 50.0)
        y1 = 10.0 + (i * 50.0)
        x2 = x1 + 40.0
        y2 = y1 + 40.0
        x3 = x2 + 80.0
        y3 = y2 + 80.0
        x4 = x3 + 90.0
        y4 = y3 + 9.0

        spots.append(Spot(
            id=Id(value=spot_id),
            coordinate=Polygon(
                corners=(
                    Coordinate(x=x1, y=y1),
                    Coordinate(x=x2, y=y2),
                    Coordinate(x=x3, y=y3),
                    Coordinate(x=x4, y=y4),
                )
            )
        ))

    return spots


@pytest.fixture
def dynamic_spots() -> Any:
    return create_spots


@pytest.fixture
def sample_spot() -> Any:
    return create_spots(1)[0]


@pytest.fixture
def sample_vehicle(
    sample_image: Any,
    sample_vehicle_details: Any,
    sample_plate: Any,
    sample_coordinate_polygon: Any
) -> Any:
    return Vehicle(
        image=sample_image,
        details=sample_vehicle_details,
        plate=sample_plate,
        coordinate=sample_coordinate_polygon
    )


@pytest.fixture
def sample_vehicle_without_plate(
    sample_image: Any,
    sample_vehicle_details: Any,
    sample_coordinate_polygon: Any
) -> Any:
    return Vehicle(
        image=sample_image,
        details=sample_vehicle_details,
        plate=None,
        coordinate=sample_coordinate_polygon
    )


@pytest.fixture
def sample_vehicle_details() -> Any:
    return VehicleDetails(
        type=VehicleType.CAR,
        color=Color.BLUE
    )


@pytest.fixture
def sample_vehicle_observed(sample_vehicle_details: Any, sample_coordinate_polygon: Any) -> Any:
    return VehicleObserved(
        details=sample_vehicle_details,
        coordinate=sample_coordinate_polygon,
        score=0.1
    )
