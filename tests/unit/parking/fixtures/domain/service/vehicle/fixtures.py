# pylint: disable=redefined-outer-name
from typing import Any
from unittest.mock import AsyncMock
import pytest

@pytest.fixture
def mock_vehicle_recognizer() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_vehicle_identifier() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_plate_identifier() -> Any:
    return AsyncMock()
