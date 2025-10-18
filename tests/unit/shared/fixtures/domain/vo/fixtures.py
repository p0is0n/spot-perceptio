# pylint: disable=redefined-outer-name
from unittest.mock import Mock
import pytest

from shared.domain.vo.data import ImageBinary

@pytest.fixture
def mock_image_binary():
    mock = Mock(spec=ImageBinary)
    mock.crop.return_value = mock
    mock.data.return_value = b"mock_image_data"

    return mock
