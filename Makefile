.PHONY: lint test ci spec-sync tlc

lint:
	ruff check .

test:
	python3 -m unittest discover -s chore_dispatcher/tests -p "test_*.py" -t .

ci: lint test tlc
	python3 scripts/check_readme_spec_sync.py

spec-sync:
	python3 scripts/check_readme_spec_sync.py

tlc:
	# Run the bounded TLC model for the workflow state machine.
	@if command -v tlc >/dev/null 2>&1; then \
		tlc spec/WORKFLOW.tla; \
	elif [ -x tools/tlc ]; then \
		./tools/tlc spec/WORKFLOW.tla; \
	else \
		mkdir -p tools; \
		curl -L -o tools/tla2tools.jar https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar; \
		printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' 'exec java -jar "$$(dirname "$$0")/tla2tools.jar" "$$@"' > tools/tlc; \
		chmod +x tools/tlc; \
		./tools/tlc spec/WORKFLOW.tla; \
	fi
