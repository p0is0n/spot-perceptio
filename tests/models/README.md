# Model Testing Suite

This directory contains the complete testing environment for validating and benchmarking machine-learning models used for **parking spot occupancy detection**, **object detection**, and related computer vision tasks.

These tests run **manually**, and operate directly on the model weights and the prepared dataset of parking lot images.

The goal of this suite is to ensure:
- high model accuracy.
- correct polygon/geometry logic.
- consistent behavior across model versions.
- reproducible evaluation.
- and easy comparison between multiple ML architectures.

#### Each test corresponds to a different evaluation strategy:

| Test File                      | Purpose |
|--------------------------------|---------|
| `test_parking_spot_crop.py`    | Crop-based detection: passes each parking spot crop to the model (oldest) |
| `test_parking_spot_no_crop.py` | Full-frame detection + geometry/polygon filtering |

---

## Dataset Description

Each image filename encodes the **ground truth occupancy status** of the spots.

#### Filename format

`<image_id><SpotID><0|1><SpotID><0|1>...`

Examples:

- `8701_A1_B0.jpg`  
  - Spot A → occupied  
  - Spot B → free  

- `5120_A0_B1.jpg`  
  - Spot A → free  
  - Spot B → occupied  

This makes the test dataset **self-annotated** and fully deterministic.

#### Ground Truth Encoding Format

For each image:

- `A1` means **Spot A is occupied**
- `A0` means **Spot A is free**
- `B1` means **Spot B is occupied**
- …

This allows test scripts to automatically parse expected labels without manual annotation files.
The number of spot-codes in the filename must match the number of configured spots in the test.

---

## Parking Spot Geometry (Polygons)

Each parking spot is represented by a `Polygon` value object:

```python
Polygon(
    corners=[
        Coordinate(x=387, y=230),
        Coordinate(x=43, y=1408),
        ...
    ]
)
```

These polygons are manually extracted from real frames and define the exact bounding area of each parking space.

Tests use these polygons to determine:
- whether a detected vehicle belongs to that spot,
- whether detections overlap,
- and how much the model respects the spatial constraints.

## Model Evaluation Strategies

#### 1. Crop-based strategy
- Each spot is cropped from the frame
- The crop is sent to the model
- Detections are interpreted only inside this crop (works well but sensitive to angled cameras and partial vehicles)

#### 2. Full-frame strategy (best)
- The model processes the full camera frame
- All vehicles are detected
- Each vehicle is matched against each spot polygon (best for cameras with skew, tilt, or partial occlusion)

### Visualization of detections
Optional visual output is written to: `tests/models/images/**/results/`

This includes:
* detected bounding boxes
* polygons of spots
* color coding for correctness
* occupancy labels

_Useful for inspecting model behavior._

## Dataset Preparation
To add more test cases:
- Capture an image from the parking camera.
- Rename it using the filename format: `<id>_<SpotID><0/1>_<SpotID><0/1>.jpg` (or for one spot).
- Ensure spot polygons remain valid for this camera angle.
- Save the image into: `tests/models/images/parking_spot/`.
- Run the tests.

### Why These Tests Matter
- Ensure ML model accuracy with real-world camera geometry
- Validate that polygon logic works under different angles
- Detect regression when updating YOLO models
- Compare performance of various architectures (YOLO11, YOLO12, OBB, etc.)
- Tune detection thresholds
- Ensure stable behavior before deploying updates
- These tests act as a lifeline for production parking detection, catching problems before they hit live environments.
