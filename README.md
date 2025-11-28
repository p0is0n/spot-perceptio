# Spot Perceptio

A lightweight image perception service based on Python, FastAPI, Uvicorn, and UltraLytics.

---

## Environment

Copy and edit the environment file:

```sh
cp .env.example .env
```

---

## Build

```sh
docker build -t spot-perceptio .
```

---

## Models

Create a folder for YOLO models and download a model:

```sh
mkdir -p models
curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt -o models/yolo11n.pt
```

---

## Run

```sh
docker run -d \
  --name spot-perceptio \
  --restart=always \
  --env-file .env \
  -p 8001:8001 \
  -v ./models:/app/models:ro \
  spot-perceptio
```
