NAME:=spot-perceptio
APP_REST:=src.app.rest.main:app

D=docker

#
# Control container
#

build-container:
	@$(D) build -t $(NAME) -f Dockerfile .

build-container-dev:
	@$(D) build -t $(NAME) -f Dockerfile.dev .

build-container-test:
	@$(D) build -t $(NAME) -f Dockerfile.test .

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

clean-container:
	@$(D) rmi -f $(NAME)

#
# Control local
#

run-rest:
	@uvicorn $(APP_REST)

run-rest-dev:
	@uvicorn $(APP_REST) --reload --log-level=debug

run-rest-test:
	@uvicorn $(APP_REST)

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
