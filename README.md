# Spot Perceptio

Spot Perceptio is an image-processing microservice built with **Python**, **FastAPI**, **Ultralytics YOLO**, and **HyperLPR**.

Designed for parking analytics, vehicle detection, and license plate recognition in smart-home and backend systems.

The project follows **Domain-Driven Design (DDD)** principles to ensure strict domain boundaries, modularity, testability, and long-term maintainability.

## Architecture Overview

The project is structured according to Domain-Driven Design principles.

This architecture provides:
- clear separation of domain, application, and infrastructure layers
- easy plug-and-play ML backends
- predictable extension points for new vision tasks
- high testability and isolation of domain logic
- a consistent and scalable development workflow

## Installation

### Create .env file or pass variables to your environment

```sh
touch .env
```

<details>
<summary>Supported env variables</summary>

```sh
APP_DEBUG=False
APP_LOG_LEVEL=trace
APP_HOST=0.0.0.0
APP_PORT=8001

YOLO_VERBOSE=False

ML_YOLO_MODEL_DEVICE=cpu

ML_VEHICLE_IDENTIFIERS=yolo
ML_VEHICLE_IDENTIFIER_YOLO_MODEL_PATH=
ML_VEHICLE_IDENTIFIER_YOLO_THRESHOLD=0.80

ML_PLATE_IDENTIFIERS=hyperlpr,yolo
ML_PLATE_IDENTIFIER_YOLO_MODEL_PATH=
ML_PLATE_IDENTIFIER_YOLO_THRESHOLD=0.10
ML_PLATE_IDENTIFIER_HYPERLPR_THRESHOLD=0.90
```
</details>

### Prepare models

```sh
mkdir -p models/ul
```

Vehicles identifier model:
```sh
curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo12s.pt -o models/ul/yolo12s.pt
```

Plates identifier model:
```sh
curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo12s.pt -o models/ul/yolo12s.pt
```

<details>
<summary>Unstable docker image build (main branch)</summary>

```sh
docker run -d \
		--name spot-perceptio \
		--restart=always \
		--env-file .env \
		-p 8001:8001 \
		-v ./models:/app/models:ro \
		ghcr.io/p0is0n/spot-perceptio:main
```

```sh
docker logs -f spot-perceptio
```
</details>

<details>
<summary>Build docker image from source</summary>

#### Clone the repository:

```sh
git clone git@github.com:p0is0n/spot-perceptio.git
```

#### Build and run:
```sh
make build-container
```

```sh
make start-container
```
</details>

## API

REST API is available at `http://127.0.0.1:8001/docs`.

## Development

The repository includes everything required to start development.
VS Code is the recommended environment.

Development features:
- Development via devcontainer
- Application source code located in /src
- Tests located in /tests
- Multiple Dockerfiles:
- - Dockerfile - production image
- - Dockerfile.dev - development environment
- - Dockerfile.test - test execution
- CI/CD pipelines powered by GitHub Actions

## Third-Party Licenses

This project depends on third-party open source libraries and models, including:

- Ultralytics YOLO - licensed under the AGPL-3.0
- HyperLPR - licensed under Apache-2.0

These dependencies are used as external runtime components and are not
distributed as part of this repository's source code.

## License

This project is licensed under the MIT License.
