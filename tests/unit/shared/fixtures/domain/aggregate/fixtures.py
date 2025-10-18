# pylint: disable=redefined-outer-name
import pytest

from shared.domain.aggregate.image import Image
from shared.domain.vo.coordinate import BoundingBox, Coordinate

@pytest.fixture
def sample_image(mock_image_binary):
    coordinate = BoundingBox(
        p1=Coordinate(x=0.0, y=0.0),
        p2=Coordinate(x=100.0, y=100.0)
    )

    return Image(data=mock_image_binary, coordinate=coordinate)
