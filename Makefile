.PHONY: help bootstrap dev test lint format format-check build version docs status benchmark validate artifact ci release clean publish

# make run       Run OptEngine quickstart only
# make test      Run pytest only
# make ci        Run the complete non-mutating quality gate
# make dev       Format, then run the complete quality gate
# make version   Preview the next version and tag from main
# make release   Trigger the official GitHub release workflow

DEV_COMMAND = FORCE_COLOR=1 uv run python tools/dev.py

define compact_step
	@printf "\033[36m> $(1)\033[0m\n"
endef

define compact_pass
	@printf "\033[32m✓ $(1) passed\033[0m\n\n"
endef

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-14s %s\n", $$1, $$2}'

bootstrap: ## Verify the toolchain and synchronize the development environment
	$(call compact_step,toolchain.python)
	@command -v python3 >/dev/null 2>&1 || { \
		printf "\033[31m✗ toolchain.python failed: python3 not found\033[0m\n\n"; \
		exit 1; \
	}
	@python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" || { \
		printf "\033[31m✗ toolchain.python failed: Python 3.10+ is required\033[0m\n"; \
		python3 --version; \
		echo ""; \
		exit 1; \
	}
	@python3 --version
	$(call compact_pass,toolchain.python)

	$(call compact_step,toolchain.git)
	@command -v git >/dev/null 2>&1 || { \
		printf "\033[31m✗ toolchain.git failed: git not found\033[0m\n\n"; \
		exit 1; \
	}
	@git --version
	$(call compact_pass,toolchain.git)

	$(call compact_step,toolchain.make)
	@command -v make >/dev/null 2>&1 || { \
		printf "\033[31m✗ toolchain.make failed: make not found\033[0m\n\n"; \
		exit 1; \
	}
	@make --version | head -n 1
	$(call compact_pass,toolchain.make)

	$(call compact_step,toolchain.uv)
	@command -v uv >/dev/null 2>&1 || { \
		printf "\033[31m✗ toolchain.uv failed: uv not found\033[0m\n"; \
		echo "Install with: brew install uv"; \
		echo ""; \
		exit 1; \
	}
	@uv --version
	$(call compact_pass,toolchain.uv)

	$(call compact_step,environment.sync)
	@uv sync || { \
		printf "\033[31m✗ environment.sync failed\033[0m\n\n"; \
		exit 1; \
	}
	$(call compact_pass,environment.sync)

run: bootstrap ## Run the OptEngine quickstart
	@uv run python demos/quickstart.py

dev: bootstrap ## Format source and run all pre-merge checks
	@$(DEV_COMMAND) dev

format: bootstrap ## Format source code
	@$(DEV_COMMAND) format

format-check: bootstrap ## Verify formatting without modifying source code
	@$(DEV_COMMAND) format-check

lint: bootstrap ## Run static analysis
	@$(DEV_COMMAND) lint

test: bootstrap ## Execute the software test suite
	@$(DEV_COMMAND) test

build: bootstrap ## Build source and wheel distributions
	@$(DEV_COMMAND) build

version: bootstrap ## Preview the next semantic version and Git tag
	@$(DEV_COMMAND) version
	
docs: ## Build or validate documentation
	@echo ""
	@echo "> docs.status"
	@echo "• documentation automation is not implemented yet"
	@echo ""

benchmark: ## Run performance benchmarks
	@echo ""
	@echo "> benchmark.status"
	@echo "• benchmark suite is not implemented yet"
	@echo ""

validate: ## Run research validation
	@echo ""
	@echo "> validation.status"
	@echo "• validation suite is not implemented yet"
	@echo ""

artifact: bootstrap ## Promote an output into the artifact registry
	@uv run python demos/promote_artifact.py

ci: bootstrap ## Run the local CI quality gate
	@$(DEV_COMMAND) ci

release-check: bootstrap ## Run complete local release-readiness checks
	@$(DEV_COMMAND) release-check

release: ## Trigger the official GitHub release workflow
	@branch="$$(git branch --show-current)"; \
	if [ "$$branch" != "main" ]; then \
		printf "\033[31m✗ release failed: current branch is '%s', expected 'main'\033[0m\n" "$$branch"; \
		exit 1; \
	fi
	@git diff --quiet && git diff --cached --quiet || { \
		printf "\033[31m✗ release failed: working tree is not clean\033[0m\n"; \
		exit 1; \
	}
	@command -v gh >/dev/null 2>&1 || { \
		printf "\033[31m✗ release failed: GitHub CLI 'gh' is not installed\033[0m\n"; \
		exit 1; \
	}
	@gh auth status >/dev/null 2>&1 || { \
		printf "\033[31m✗ release failed: GitHub CLI is not authenticated\033[0m\n"; \
		exit 1; \
	}
	@git fetch origin main
	@test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || { \
		printf "\033[31m✗ release failed: local main does not match origin/main\033[0m\n"; \
		exit 1; \
	}
	@printf "\033[36m> release.github\033[0m\n"
	@gh workflow run release.yml --ref main
	@printf "\033[32m✓ release workflow dispatched\033[0m\n\n"

clean: ## Remove disposable generated files and caches
	@find outputs -type f ! -name ".gitkeep" -delete
	@rm -rf .pytest_cache .ruff_cache
	@rm -rf build dist
	@find . -maxdepth 1 -name "*.egg-info" -type d -exec rm -rf {} +
	@find . -name "__pycache__" -type d -exec rm -rf {} +

publish: 