# pylint: disable=redefined-outer-name
from typing import Any

import pytest

from shared.domain.aggregate.image import Image

@pytest.fixture
def sample_image(mock_data_image_binary: Any, sample_coordinate_polygon: Any) -> Any:
    return Image(data=mock_data_image_binary, coordinate=sample_coordinate_polygon)
