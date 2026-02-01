.PHONY: lint test ci spec-sync

lint:
	ruff check .

test:
	python -m unittest discover -s chore_dispatcher/tests

ci: lint test
	python scripts/check_readme_spec_sync.py

spec-sync:
	python scripts/check_readme_spec_sync.py
