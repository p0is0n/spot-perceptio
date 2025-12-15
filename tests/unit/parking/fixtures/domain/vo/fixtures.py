# pylint: disable=redefined-outer-name
import random
from typing import Any

import pytest
from faker import Faker

from shared.domain.enum.country import Country
from parking.domain.vo.plate import Plate

@pytest.fixture
def sample_plate(
    sample_coordinate_polygon: Any,
    faker: Faker
) -> Any:
    return Plate(
        value=faker.license_plate(),
        country=random.choice(list(Country)),
        coordinate=sample_coordinate_polygon
    )
