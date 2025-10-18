# pylint: disable=redefined-outer-name
import pytest

from shared.domain.vo.base import Id
from shared.domain.aggregate.spot import Spot
from shared.domain.vo.coordinate import BoundingBox, Coordinate

from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails
from parking.domain.enum.vehicle import VehicleType
from parking.domain.enum.color import Color

def create_spots(count: int, prefix_id: str = "test-spot"):
    spots = []

    for i in range(count):
        spot_id = f"{prefix_id}-{i+1}"
        x1 = 10.0 + (i * 50.0)
        y1 = 10.0 + (i * 50.0)
        x2 = x1 + 40.0
        y2 = y1 + 40.0

        spots.append(Spot(
            id=Id(spot_id),
            coordinate=BoundingBox(
                p1=Coordinate(x=x1, y=y1),
                p2=Coordinate(x=x2, y=y2)
            )
        ))

    return spots


@pytest.fixture
def dynamic_spots():
    return create_spots

@pytest.fixture
def sample_spot():
    return create_spots(1)[0]


@pytest.fixture
def sample_vehicle(sample_image, sample_vehicle_details, sample_plate):
    return Vehicle(
        image=sample_image,
        details=sample_vehicle_details,
        plate=sample_plate
    )


@pytest.fixture
def sample_vehicle_without_plate(sample_image, sample_vehicle_details):
    return Vehicle(
        image=sample_image,
        details=sample_vehicle_details,
        plate=None
    )


@pytest.fixture
def sample_vehicle_details():
    return VehicleDetails(
        type=VehicleType.CAR,
        color=Color.BLUE
    )
