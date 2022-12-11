.PHONY: help
help:
	@echo "Read the makefile"

.PHONY: up
up:
	pip-compile

.PHONY: deps
deps:
	pip-sync

.PHONY: lint
lint:
	isort .
	black .
