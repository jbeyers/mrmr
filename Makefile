.PHONY: help
help:
	@echo "Read the makefile"

.PHONY: up
up:
	pip-compile > requirements.txt

.PHONY: deps
deps:
	pip-sync

.PHONY: lint
lint:
	isort .
	black .
