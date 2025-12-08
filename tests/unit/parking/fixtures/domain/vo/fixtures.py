# pylint: disable=redefined-outer-name
from typing import Any

import pytest
from faker import Faker

from parking.domain.vo.plate import Plate

@pytest.fixture
def sample_plate(
    sample_coordinate_polygon: Any,
    faker: Faker
) -> Any:
    return Plate(
        value=faker.license_plate(),
        country=faker.country_code(),
        coordinate=sample_coordinate_polygon
    )
