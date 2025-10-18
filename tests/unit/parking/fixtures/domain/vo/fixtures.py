# pylint: disable=redefined-outer-name
import pytest

from parking.domain.vo.plate import Plate

@pytest.fixture
def sample_plate():
    return Plate(value="ABC123", country="US")
