.PHONY: lint test ci

lint:
	ruff check .

test:
	python -m unittest discover -s chore_dispatcher/tests

ci: lint test
