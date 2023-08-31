SHELL=/bin/bash
.DEFAULT_GOAL := default

.PHONY: install
install:
	@echo "Installing Production Dependencies."
	pip install -e .

.PHONY: install-dev
install-dev:
	@echo "Installing Development Dependencies."
	pip install -e .[dev]
	pre-commit install

.PHONY: lint
lint:
	SKIP=no-commit-to-branch pre-commit run --all-files


.PHONY: test
test:
ifeq ($(DB_HOST),localhost)
	@echo "Flush db."
	python tests/setup/teardown.py
	@echo "Insert test data."
	python tests/setup/setup.py
	@echo "Test is running..."
	python -m pytest -lv ${ARGS}
else
	@echo "Skipping tests because DB_HOST is not localhost."
endif

.PHONY: coverage
coverage:
	@echo "Test coverage."
	python -m coverage run --source=src -m pytest -lv ${ARGS}
	python -m coverage report -m
