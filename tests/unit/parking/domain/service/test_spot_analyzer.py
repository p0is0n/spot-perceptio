# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
from typing import Any

import pytest

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.aggregate.spot import ParkingSpot
from shared.domain.aggregate.image import Image

from tests.unit.shared.fixtures.domain.aggregate.fixtures import sample_image
from tests.unit.shared.fixtures.domain.vo.fixtures import (
    sample_coordinate_polygon,
    mock_data_image_binary
)
from tests.unit.parking.fixtures.domain.service.vehicle.fixtures import mock_vehicle_recognizer
from tests.unit.parking.fixtures.domain.vo.fixtures import sample_plate
from tests.unit.parking.fixtures.domain.aggregate.fixtures import (
    dynamic_spots,
    sample_spot,
    sample_vehicle,
    sample_vehicle_without_plate,
    sample_vehicle_details
)

@pytest.mark.unit
class TestSpotAnalyzer:
    """Test cases for SpotAnalyzer service"""

    @pytest.mark.asyncio
    async def test_analyze_with_vehicle(
        self,
        mock_vehicle_recognizer: Any,
        sample_image: Any,
        sample_spot: Any,
        sample_vehicle: Any
    ) -> Any:
        """Test analyze method when vehicle is detected"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = sample_vehicle

        result = await analyzer.analyze(sample_image, sample_spot)
        mock_vehicle_recognizer.recognize.assert_called_once()

        assert isinstance(result, ParkingSpot)
        assert result.occupied is True
        assert result.spot == sample_spot
        assert result.vehicle == sample_vehicle

    @pytest.mark.asyncio
    async def test_analyze_without_vehicle(
        self,
        mock_vehicle_recognizer: Any,
        sample_image: Any,
        sample_spot: Any
    ) -> Any:
        """Test analyze method when no vehicle is detected"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = None

        result = await analyzer.analyze(sample_image, sample_spot)
        mock_vehicle_recognizer.recognize.assert_called_once()

        assert isinstance(result, ParkingSpot)
        assert result.occupied is False
        assert result.spot == sample_spot
        assert result.vehicle is None

    @pytest.mark.asyncio
    async def test_analyze_image_correctly(
        self,
        mock_vehicle_recognizer: Any,
        sample_image: Any,
        sample_spot: Any
    ) -> Any:
        """Test that analyze method image using spot coordinates"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = None

        result = await analyzer.analyze(sample_image, sample_spot)
        mock_vehicle_recognizer.recognize.assert_called_once()

        image = mock_vehicle_recognizer.recognize.call_args.args[0]
        coordinate = mock_vehicle_recognizer.recognize.call_args.args[1]

        assert isinstance(result, ParkingSpot)
        assert isinstance(image, Image)
        assert coordinate == sample_spot.coordinate

    @pytest.mark.asyncio
    async def test_analyze_handles_recognizer_exception(
        self,
        mock_vehicle_recognizer: Any,
        sample_image: Any,
        sample_spot: Any
    ) -> Any:
        """Test analyze method handles VehicleRecognizer exceptions"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.side_effect = Exception("Recognition failed")

        with pytest.raises(Exception, match="Recognition failed"):
            await analyzer.analyze(sample_image, sample_spot)

    @pytest.mark.asyncio
    async def test_analyze_multiple_spots(
        self,
        mock_vehicle_recognizer: Any,
        sample_image: Any,
        dynamic_spots: Any
    ) -> Any:
        """Test analyze method with multiple different spots"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = None

        spots = dynamic_spots(5)
        spots_results = []
        for spot in spots:
            spots_results.append(await analyzer.analyze(sample_image, spot))

        for i, spot in enumerate(spots):
            assert spots_results[i].occupied is False
            assert spots_results[i].spot == spot

        assert mock_vehicle_recognizer.recognize.call_count == len(spots)
