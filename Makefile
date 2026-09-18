UV= uv
PYTHON = $(UV) run --active python3

export UV_CACHE_DIR := /goinfre/$(USER)/.cache/uv
export UV_LINK_MODE := copy
export HF_HOME := /goinfre/$(USER)/.cache/huggingface


all: install run


install:
	$(UV) sync --active

run:
	$(PYTHON) -m src

lint:
	@$(PYTHON) -m flake8 .
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@$(PYTHON) -m mypy . --strict
	@$(PYTHON) -m flake8 .

debug:
	@$(PYTHON) -m pdb -m src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f data/output/function_calling_results.json
	rm -fr .mypy_cache
	rm -fr .venv

.PHONY: all install run lint lint-strict debug clean
