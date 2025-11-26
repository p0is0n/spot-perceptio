# pylint: disable=redefined-outer-name
from typing import Any
from unittest.mock import Mock
from faker import Faker
import pytest

from shared.domain.vo.coordinate import Coordinate, BoundingBox, Polygon
from shared.domain.vo.data import ImageBinary

@pytest.fixture
def sample_coordinate_bounding_box(faker: Faker) -> Any:
    return BoundingBox(
        p1=Coordinate(x=faker.random_int(1, 50), y=faker.random_int(1, 50)),
        p2=Coordinate(x=faker.random_int(50, 100), y=faker.random_int(50, 100))
    )


@pytest.fixture
def sample_coordinate_polygon(faker: Faker) -> Any:
    return Polygon(
        corners=(
            Coordinate(x=faker.random_int(1, 50), y=faker.random_int(1, 50)),
            Coordinate(x=faker.random_int(1, 50), y=faker.random_int(1, 50)),
            Coordinate(x=faker.random_int(1, 50), y=faker.random_int(1, 50)),
        )
    )


@pytest.fixture
def mock_data_image_binary(faker: Faker) -> Any:
    mock = Mock(spec=ImageBinary)
    mock.crop.return_value = mock
    mock.data.return_value = faker.binary(8)

    return mock
