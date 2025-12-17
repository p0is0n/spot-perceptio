NAME:=spot-perceptio
APP_REST:=src.app.rest.main:app

D=docker

ifneq ("$(wildcard .env)","")
	include .env
	export
endif

#
# Control container
#

build-container:
	@$(D) build -t "$(NAME)" -f Dockerfile .

build-container-dev:
	@$(D) build -t "$(NAME)-dev" -f Dockerfile.dev .

build-container-test:
	@$(D) build -t "$(NAME)-test" -f Dockerfile.test .

start-container:
	@$(D) run -d \
		--name "$(NAME)" \
		--restart=always \
		--env-file .env \
		-p $(APP_PORT):$(APP_PORT) \
		-v ./models:/app/models:ro \
		"$(NAME)"

stop-container:
	@$(D) stop "$(NAME)"

remove-container:
	@$(D) rm -f "$(NAME)"

restart-container: stop-container remove-container start-container

run-in-container:
	@if [ -z "$(CMD)" ]; then \
		echo "Error: provide CMD, e.g. make run-in-container CMD='bash'"; \
		exit 1; \
	fi && \
	$(D) run --rm \
		--name $(NAME) \
		-w /app \
		$(NAME) \
		$(if $(CMD),$(CMD),exit)

run-in-container-test:
	@if [ -z "$(CMD)" ]; then \
		echo "Error: provide CMD, e.g. make run-in-container CMD='bash'"; \
		exit 1; \
	fi && \
	$(D) run --rm \
		--name "$(NAME)-test" \
		-w /app \
		"$(NAME)-test" \
		$(if $(CMD),$(CMD),exit)

clean-container:
	@$(D) rmi -f $(NAME)

#
# Control local
#

run-rest:
	@uvicorn $(APP_REST) --port $(APP_PORT) --log-level=$(APP_LOG_LEVEL)

run-rest-dev:
	@uvicorn $(APP_REST) --port $(APP_PORT) --reload --log-level=$(APP_LOG_LEVEL)

run-rest-test:
	@uvicorn $(APP_REST) --port $(APP_PORT) --log-level=$(APP_LOG_LEVEL)

clean-cache:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.pyc' -delete

#
# Check
#

lint:
	@pylint -j 0 \
		--recursive=y \
		--output-format=colorized \
		--reports=n \
		--score=y \
		--jobs=0 \
		--verbose \
		src/**/*.py \
		tests/unit/**/*.py

type-check:
	@mypy --exclude-gitignore \
		--no-color-output \
		./

test: test-unit

test-unit:
	@pytest -m unit

test-unit-cov:
	@pytest --cov=src/ --cov-report=term-missing --cov-report html -m unit

check: lint type-check
