phony: up
up:
	pip-compile

phony: deps
deps:
	pip-sync

phony: lint
lint:
	isort .
	black .
