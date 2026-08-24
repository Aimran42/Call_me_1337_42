PYTHON = python3

run:
	$(PYTHON) -m src
install:
	$(PYTHON) -m pip install --break-system-packages -q flake8 mypy

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f data/output/function_calling_results.json
	rm -rf .mypy_cache *.lock

.PHONY: install run clean lint lint-strict