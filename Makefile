run-rest-dev:
	@uvicorn src.app.rest.main:app --reload

run-rest-prod:
	@uvicorn src.app.rest.main:app

clean-cache:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.pyc' -delete

lint:
	@pylint -j 0 \
		--recursive=y \
		--output-format=colorized \
		--reports=n \
		--score=n \
		src/**/*.py \
		tests/unit/**/*.py

test: test-unit

test-unit:
	@pytest -m unit
