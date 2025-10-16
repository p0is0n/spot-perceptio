run-rest-dev:
	@uvicorn src.app.rest.main:app --reload

run-rest-prod:
	@uvicorn src.app.rest.main:app

clean-cache:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.pyc' -delete

lint:
	@pylint src/
