# Spot Perceptio

Spot Perceptio is an image-processing microservice built with **Python**, **FastAPI**, and **Ultralytics**.

The project follows a **Domain-Driven Design (DDD)** architecture to ensure clear domain boundaries, modularity, and maintainability.

## Architecture Overview

The project is organized according to Domain-Driven Design principles.

This structure allows:
- clean boundaries  
- plug-and-play ML backends  
- easy unit testing  
- extensibility for new vision tasks  
- predictable development workflow  

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

#### Download a model into a folder:
```sh
mkdir -p models/ul
```

```sh
curl -L \
  https://github.com/ultralytics/assets/releases/download/v8.3.0 yolo12s.pt -o models/ul/yolo12s.pt
```

_You can choose another model (don't forget to update the `.env` file accordingly)._

#### Build and run:
```sh
docker build -t spot-perceptio .
```

```sh
docker run -d \
  --name spot-perceptio \
  --restart=always \
  --env-file .env \
  -p 8001:8001 \
  -v ./models:/app/models:ro \
  spot-perceptio
```
