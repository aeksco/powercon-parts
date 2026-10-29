# Usage: make [MODEL=example] <target>
MODEL ?= example
RUN   := uv run python

# Outputs are grouped by type: build/<type>/<model>.<type>
OUTPUTS := build/stl/$(MODEL).stl build/step/$(MODEL).step build/obj/$(MODEL).obj build/png/$(MODEL).png
MODELS  := $(patsubst models/%.py,%,$(filter-out models/__init__.py,$(wildcard models/*.py)))

.PHONY: all stl step obj png all-models setup view clean list help

all: $(OUTPUTS) ## Export STL + STEP + OBJ + isometric PNG for MODEL (default: example)

stl: build/stl/$(MODEL).stl ## Export STL only
step: build/step/$(MODEL).step ## Export STEP only
obj: build/obj/$(MODEL).obj ## Export OBJ only
png: build/png/$(MODEL).png ## Export isometric render only

# All outputs come from one run; rebuild when any model, library or script changes
# (assemblies import other models, so track them all).
$(OUTPUTS): $(wildcard models/*.py) $(wildcard lib/*.py) scripts/export.py scripts/render.py
	$(RUN) scripts/export.py $(MODEL)

all-models: ## Export every model in models/
	@for m in $(MODELS); do $(MAKE) --no-print-directory MODEL=$$m || exit 1; done

setup: ## Install dependencies into .venv
	uv sync

view: ## Export and show in the OCP viewer (needs `python -m ocp_vscode` or the VS Code extension)
	$(RUN) scripts/export.py $(MODEL) --view

list: ## List available models
	@for m in $(MODELS); do echo $$m; done

clean: ## Remove build outputs
	rm -rf build

help: ## Show targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'
