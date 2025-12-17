# Spot Perceptio

Spot Perceptio is an image-processing microservice built with **Python**, **FastAPI**, **Ultralytics YOLO**, and **HyperLPR**.

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

### From source

#### Clone the repository:

```sh
git clone git@github.com:p0is0n/spot-perceptio.git
```

#### Copy the example environment file:

```sh
cp .env.example .env
```

_You can modify the `.env` file to suit your needs._

#### Download and prepare models:
```sh
mkdir -p models/ul
```

```sh
curl -L \
  https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo12s.pt -o models/ul/yolo12s.pt
```

_You can choose another model (don't forget to update the `.env` file accordingly)._

#### Build and run:
```sh
make build-container
```

```sh
make start-container
```

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
