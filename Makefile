.PHONY: lint test ci spec-sync tlc

lint:
	ruff check .

test:
	python3 -m unittest discover -s chore_dispatcher/tests -p "test_*.py" -t .

ci: lint test tlc
	python scripts/check_readme_spec_sync.py

spec-sync:
	python scripts/check_readme_spec_sync.py

tlc:
	# Run the bounded TLC model for the workflow state machine.
	tlc spec/WORKFLOW.tla
