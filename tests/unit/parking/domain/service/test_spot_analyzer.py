# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
import pytest

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.aggregate.spot import ParkingSpot
from shared.domain.aggregate.image import Image

from tests.unit.shared.fixtures.domain.aggregate.fixtures import sample_image
from tests.unit.shared.fixtures.domain.vo.fixtures import mock_image_binary
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
        mock_vehicle_recognizer,
        sample_image,
        sample_spot,
        sample_vehicle
    ):
        """Test analyze method when vehicle is detected"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = sample_vehicle

        result = await analyzer.analyze(sample_image, sample_spot)

        assert isinstance(result, ParkingSpot)
        assert result.occupied is True
        assert result.spot == sample_spot
        assert result.vehicle == sample_vehicle

        mock_vehicle_recognizer.recognize.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_without_vehicle(
        self,
        mock_vehicle_recognizer,
        sample_image,
        sample_spot
    ):
        """Test analyze method when no vehicle is detected"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = None

        result = await analyzer.analyze(sample_image, sample_spot)

        assert isinstance(result, ParkingSpot)
        assert result.occupied is False
        assert result.spot == sample_spot
        assert result.vehicle is None

        mock_vehicle_recognizer.recognize.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_crops_image_correctly(
        self,
        mock_vehicle_recognizer,
        sample_image,
        sample_spot
    ):
        """Test that analyze method crops image using spot coordinates"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.return_value = None

        await analyzer.analyze(sample_image, sample_spot)

        sample_image.data.crop.assert_called_once_with(sample_spot.coordinate)
        mock_vehicle_recognizer.recognize.assert_called_once()

        call_args = mock_vehicle_recognizer.recognize.call_args[0]
        cropped_image = call_args[0]

        assert len(call_args) == 1
        assert isinstance(cropped_image, Image)
        assert cropped_image.coordinate == sample_spot.coordinate

    @pytest.mark.asyncio
    async def test_analyze_handles_recognizer_exception(
        self,
        mock_vehicle_recognizer,
        sample_image,
        sample_spot
    ):
        """Test analyze method handles VehicleRecognizer exceptions"""
        analyzer = SpotAnalyzer(mock_vehicle_recognizer)
        mock_vehicle_recognizer.recognize.side_effect = Exception("Recognition failed")

        with pytest.raises(Exception, match="Recognition failed"):
            await analyzer.analyze(sample_image, sample_spot)

    @pytest.mark.asyncio
    async def test_analyze_multiple_spots(
        self,
        mock_vehicle_recognizer,
        sample_image,
        dynamic_spots
    ):
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
