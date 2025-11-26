# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
from typing import Any

import pytest

from parking.domain.service.vehicle.recognizer import VehicleRecognizer
from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails
from parking.domain.vo.plate import Plate

from tests.unit.shared.fixtures.domain.aggregate.fixtures import sample_image
from tests.unit.shared.fixtures.domain.vo.fixtures import (
    sample_coordinate_polygon,
    mock_data_image_binary
)
from tests.unit.parking.fixtures.domain.service.vehicle.fixtures import (
    mock_vehicle_identifier,
    mock_plate_identifier
)
from tests.unit.parking.fixtures.domain.aggregate.fixtures import (
    sample_vehicle_details,
    sample_vehicle,
    sample_vehicle_without_plate
)
from tests.unit.parking.fixtures.domain.vo.fixtures import sample_plate

@pytest.mark.unit
class TestVehicleRecognizer:
    """Test cases for VehicleRecognizer service"""

    @pytest.mark.asyncio
    async def test_recognize_with_vehicle_and_plate(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any,
        sample_vehicle_details: Any,
        sample_plate: Any
    ) -> Any:
        """Test recognize method when both vehicle and plate are detected"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = sample_vehicle_details
        mock_plate_identifier.identify.return_value = sample_plate

        result = await recognizer.recognize(sample_image)

        assert isinstance(result, Vehicle)
        assert result.image == sample_image
        assert result.details == sample_vehicle_details
        assert result.plate == sample_plate

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_called_once_with(sample_image)

    @pytest.mark.asyncio
    async def test_recognize_with_vehicle_no_plate(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any,
        sample_vehicle_details: Any
    ) -> Any:
        """Test recognize method when vehicle is detected but no plate"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = sample_vehicle_details
        mock_plate_identifier.identify.return_value = None

        result = await recognizer.recognize(sample_image)

        assert isinstance(result, Vehicle)
        assert result.image == sample_image
        assert result.details == sample_vehicle_details
        assert result.plate is None

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_called_once_with(sample_image)

    @pytest.mark.asyncio
    async def test_recognize_no_vehicle_detected(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any
    ) -> Any:
        """Test recognize method when no vehicle is detected"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = None

        result = await recognizer.recognize(sample_image)

        assert result is None

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_not_called()

    @pytest.mark.asyncio
    async def test_recognize_with_multiple_images(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any,
        sample_vehicle_details: Any,
        sample_plate: Any
    ) -> Any:
        """Test recognize method with multiple different images"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = sample_vehicle_details
        mock_plate_identifier.identify.return_value = sample_plate

        results = []
        for _ in range(3):
            results.append(await recognizer.recognize(sample_image))

        for result in results:
            assert isinstance(result, Vehicle)
            assert result.image == sample_image
            assert result.details == sample_vehicle_details
            assert result.plate == sample_plate

        assert mock_vehicle_identifier.identify.call_count == 3
        assert mock_plate_identifier.identify.call_count == 3

    @pytest.mark.asyncio
    async def test_recognize_vehicle_identifier_exception(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any
    ) -> Any:
        """Test recognize method when vehicle identifier raises exception"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.side_effect = Exception("Vehicle identification failed")

        with pytest.raises(Exception, match="Vehicle identification failed"):
            await recognizer.recognize(sample_image)

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_not_called()

    @pytest.mark.asyncio
    async def test_recognize_plate_identifier_exception(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any,
        sample_vehicle_details: Any
    ) -> Any:
        """Test recognize method when plate identifier raises exception"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = sample_vehicle_details
        mock_plate_identifier.identify.side_effect = Exception("Plate identification failed")

        with pytest.raises(Exception, match="Plate identification failed"):
            await recognizer.recognize(sample_image)

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_called_once_with(sample_image)


    @pytest.mark.asyncio
    async def test_recognize_edge_case_empty_vehicle_details(
        self,
        mock_vehicle_identifier: Any,
        mock_plate_identifier: Any,
        sample_image: Any
    ) -> Any:
        """Test recognize method with edge case of empty vehicle details"""
        recognizer = VehicleRecognizer(mock_vehicle_identifier, mock_plate_identifier)
        mock_vehicle_identifier.identify.return_value = None

        result = await recognizer.recognize(sample_image)

        assert result is None

        mock_vehicle_identifier.identify.assert_called_once_with(sample_image)
        mock_plate_identifier.identify.assert_not_called()
