## **Project Context**
You are working on a Python project with Domain-Driven Design (DDD) architecture using:
- **FastAPI** for REST API
- **pytest** with async support
- **Bounded contexts**: learn folders at src/*
- **Layers**: Domain, Application, Infrastructure, UI
- **Patterns**: Aggregates, Value Objects, Services, Protocols, Handlers

## **Test Structure Requirements**

### **Directory Structure**
```
tests/unit/
├── __init__.py
├── conftest.py (main configs for all tests)
├── {bounded_context}/
│   ├── domain/
│   │   ├── service/
│   │   │   └── test_{service_name}.py
│   │   ├── aggregate/
│   │   │   └── test_{aggregate_name}.py
│   │   └── vo/
│   │       └── test_{vo_name}.py
│   └── fixtures/
│       └── domain/
│           ├── aggregate/
│           │   └── fixtures.py
│           ├── service/
│           │   └── {service_name}/
│           │       └── fixtures.py
│           └── vo/
│               └── fixtures.py
```

### **Fixture Organization Principles**

1. **Domain-specific fixtures** go in `{bounded_context}/fixtures/`
2. **Shared fixtures** go in `shared/fixtures/`
3. **Factory functions** for dynamic creation
4. **Mock fixtures** for external dependencies
5. **Sample data fixtures** for common test objects
6. **Private data** don't test private methods and properties
### **Fixture File Example Structure**

```python
# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
import pytest
from unittest.mock import AsyncMock, Mock

from {bounded_context}.domain.aggregate.{aggregate} import {Aggregate}
from {bounded_context}.domain.vo.{vo} import {ValueObject}

# Factory functions (not fixtures)
def create_{objects}(count: int, prefix_id: str = "test-{object}"):
    """Helper function to create N objects dynamically"""
    objects = []
    for i in range(count):
        objects.append({Object}(
            id=Id(f"{prefix_id}-{i+1}"),
            # ... other properties
        ))
    return objects

# Factory fixtures
@pytest.fixture
def dynamic_{objects}():
    return create_{objects}

@pytest.fixture
def sample_{object}():
    return create_{objects}(1)[0]

# Sample data fixtures
@pytest.fixture
def sample_{aggregate}(dependencies...):
    return {Aggregate}(...)

# Mock fixtures
@pytest.fixture
def mock_{service}():
    return AsyncMock()
```

### **Test File Example Structure**

```python
# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
import pytest

from {bounded_context}.domain.service.{service} import {Service}

# Fixture imports (explicit paths)
from tests.unit.shared.fixtures.domain.aggregate.fixtures import sample_image
from tests.unit.{bounded_context}.fixtures.domain.service.{type}.fixtures import mock_{service}
from tests.unit.{bounded_context}.fixtures.domain.aggregate.fixtures import (
    dynamic_{objects},
    sample_{object},
    sample_{aggregate}
)

@pytest.mark.unit
class Test{Service}:
    """Test cases for {Service} service"""

    @pytest.mark.asyncio
    async def test_{method}_success(self, dependencies...):
        """Test {method} method when operation succeeds"""
        service = {Service}(dependencies...)
        result = await service.{method}(...)

        assert result is not None

    @pytest.mark.asyncio
    async def test_{method}_with_multiple_{objects}(
        self, 
        dependencies...,
        dynamic_{objects}
    ):
        """Test {method} method with multiple {objects}"""
        service = {Service}(dependencies...)
        
        objects = dynamic_{objects}(5)
        results = []
        for obj in objects:
            results.append(await service.{method}(...))
        
        for i, obj in enumerate(objects):
            assert results[i].{property} == expected_value
        
        assert mock_service.call_count == len(objects)
```

### **Coding Style Requirements**

1. **Imports**: Use explicit fixture paths, not relative imports
2. **Naming**: 
   - Test classes: `Test{ServiceName}`
   - Test methods: `test_{method}_{scenario}`
   - Fixtures: `sample_{object}`, `mock_{service}`, `dynamic_{objects}`
3. **Pylint**: Disable `unused-import,redefined-outer-name`
4. **Async**: Use `@pytest.mark.asyncio` for async tests and async methods
5. **Markers**: Use `@pytest.mark.unit` for all unit tests
6. **Documentation**: Include docstrings for all test methods
7. **Assertions**: Use descriptive assertions with clear expected values
8. **Mock verification**: Always verify mock call counts and arguments
9. **Comments and docstrings**: No add many comments to files, only as in examples. Only in english

### **Dynamic Object Creation Pattern**

```python
# Factory function
def create_{objects}(count: int, prefix_id: str = "test-{object}"):
    objects = []
    for i in range(count):
        spot_id = f"{prefix_id}-{i+1}"
        x1 = 10.0 + (i * 50.0)
        y1 = 10.0 + (i * 50.0)
        x2 = x1 + 40.0
        y2 = y1 + 40.0
        
        objects.append({Object}(
            id=Id(spot_id),
            coordinate=BoundingBox(
                p1=Coordinate(x=x1, y=y1),
                p2=Coordinate(x=x2, y=y2)
            )
        ))
    return objects

# Factory fixture
@pytest.fixture
def dynamic_{objects}():
    return create_{objects}
```

### **Test Scenarios to Cover**

1. **Success cases**: Normal operation with valid inputs
2. **Edge cases**: Empty results, None values
3. **Error handling**: Exception scenarios
4. **Multiple objects**: Dynamic creation and processing
5. **Mock verification**: Call counts, arguments, side effects
6. **Type checking**: Instance validation
7. **State verification**: Object properties and relationships
8. **Check your code**: Check your code with pylint in your mine
### **Example Test Method Pattern**

```python
@pytest.mark.asyncio
async def test_{method}_{scenario}(
    self,
    mock_dependency,
    sample_input,
    dynamic_objects
):
    """Test {method} method when {scenario}"""
    service = {Service}(mock_dependency)
    mock_dependency.{method}.return_value = expected_result
    
    result = await service.{method}(sample_input)
    

    assert isinstance(result, ExpectedType)
    assert result.{property} == expected_value
    mock_dependency.{method}.assert_called_once()
```

### **Configuration**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-v"
]
markers = [
    "unit: Unit tests"
]
asyncio_mode = "auto"
```

## **Task**
Create comprehensive unit tests following this exact structure, style, and patterns for any given domain service, aggregate, or value object. Ensure all fixtures are properly organized, tests cover all scenarios, and the code follows the established conventions.

## **Real Example from Project**

### **Fixture File**: `tests/unit/parking/fixtures/domain/aggregate/fixtures.py`
```python
# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
import pytest

from shared.domain.vo.base import Id
from shared.domain.aggregate.spot import Spot
from shared.domain.vo.coordinate import BoundingBox, Coordinate

from parking.domain.aggregate.vehicle import Vehicle, VehicleDetails
from parking.domain.enum.vehicle import VehicleType
from parking.domain.enum.color import Color

def create_spots(count: int, prefix_id: str = "test-spot"):
    spots = []

    for i in range(count):
        spot_id = f"{prefix_id}-{i+1}"
        x1 = 10.0 + (i * 50.0)
        y1 = 10.0 + (i * 50.0)
        x2 = x1 + 40.0
        y2 = y1 + 40.0

        spots.append(Spot(
            id=Id(spot_id),
            coordinate=BoundingBox(
                p1=Coordinate(x=x1, y=y1),
                p2=Coordinate(x=x2, y=y2)
            )
        ))

    return spots

@pytest.fixture
def dynamic_spots():
    return create_spots

@pytest.fixture
def sample_spot():
    return create_spots(1)[0]

@pytest.fixture
def sample_vehicle(sample_image, sample_vehicle_details, sample_plate):
    return Vehicle(
        image=sample_image,
        details=sample_vehicle_details,
        plate=sample_plate
    )

@pytest.fixture
def sample_vehicle_details():
    return VehicleDetails(
        type=VehicleType.CAR,
        color=Color.BLUE
    )
```

### **Test File**: `tests/unit/parking/domain/service/test_spot_analyzer.py`
```python
# pylint: disable=unused-import,redefined-outer-name,too-many-positional-arguments
import pytest

from parking.domain.service.spot.analyzer import SpotAnalyzer
from parking.domain.aggregate.spot import ParkingSpot
from shared.domain.aggregate.image import Image

from tests.unit.shared.fixtures.domain.aggregate.fixtures import sample_image
from tests.unit.parking.fixtures.domain.service.vehicle.fixtures import mock_vehicle_recognizer
from tests.unit.parking.fixtures.domain.aggregate.fixtures import (
    dynamic_spots,
    sample_spot,
    sample_vehicle
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
    async def test_analyze_with_multiple_spots(
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
```
