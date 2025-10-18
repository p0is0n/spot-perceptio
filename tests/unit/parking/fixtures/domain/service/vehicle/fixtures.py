# pylint: disable=redefined-outer-name
from unittest.mock import AsyncMock
import pytest

@pytest.fixture
def mock_vehicle_recognizer():
    return AsyncMock()

@pytest.fixture
def mock_vehicle_identifier():
    return AsyncMock()

@pytest.fixture
def mock_plate_identifier():
    return AsyncMock()
