PY ?= .venv/bin/python
.PHONY: setup check test dry-run run report
setup:
	python3 -m venv .venv && $(PY) -m pip install -q -e .
check:
	$(PY) -m bench check
test:
	$(PY) -m pytest -q
dry-run:
	$(PY) -m bench run --dry-run --fresh --runs 1
run:
	$(PY) -m bench run --fresh
report:
	$(PY) -m bench report
