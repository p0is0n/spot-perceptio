ARG PYTHON_VERSION=3.11

FROM --platform=$BUILDPLATFORM python:${PYTHON_VERSION}-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev --no-cache --no-interaction --no-ansi \
    && rm -rf /root/.cache/pypoetry \
        /root/.cache/pip

FROM python:${PYTHON_VERSION}-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

ENV APP_HOST=0.0.0.0 \
    APP_PORT=8001 \
    APP_LOG_LEVEL=info \
    HOME=/app \
    YOLO_CONFIG_DIR=/app/.ultralytics \
    HYPERLPR_CONFIG_DIR=/app/.hyperlpr3 \
    ORT_LOGGING_LEVEL=ERROR \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH="/app/src"

WORKDIR /app

RUN addgroup --system app \
    && adduser --disabled-password --system --ingroup app app \
    && mkdir ${YOLO_CONFIG_DIR} \
    && mkdir ${HYPERLPR_CONFIG_DIR}

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./src /app/src

RUN chown -R app:app /app
USER app

HEALTHCHECK --interval=30s --timeout=3s --retries=1 \
    CMD curl -f http://127.0.0.1:${APP_PORT}/system/health || exit 1

CMD ["sh", "-c", "exec uvicorn app.rest.main:app --host $APP_HOST --port $APP_PORT --log-level $APP_LOG_LEVEL --workers 1"]
