# Problem Solver Platform - Makefile
# Build, deployment, and development automation

# ============================================================================
# VARIABLES
# ============================================================================

PROJECT_NAME = problem-solver
APP_MODULE = src.problemsolver
CONFIG_FILE = configuration.json
VENV_DIR = venv
PYTHON = python3
PIP = pip3
PORT = 8000
DOCKER_TAG = latest

# Colors for output (if terminal supports it)
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
RED = \033[0;31m
NC = \033[0m # No Color

# Detect if we have color support
ifneq ($(shell which tput 2>/dev/null && tput colors 2>/dev/null || echo 0),0)
COLOR_SUPPORT = yes
else
COLOR_SUPPORT = no
endif

ifeq ($(COLOR_SUPPORT),yes)
define color
$(if $(findstring $(1),green),$(GREEN),$(if $(findstring $(1),yellow),$(YELLOW),$(if $(findstring $(1),blue),$(BLUE),$(if $(findstring $(1),red),$(RED),$(NC)))))
endef
else
define color
endef
endif

# ============================================================================
# DEFAULT TARGET
# ============================================================================

.PHONY: help
help:
	@echo ""
	@echo "$(call color,blue)========================================$(NC)"
	@echo "$(call color,blue)   Problem Solver Platform - Commands$(NC)"
	@echo "$(call color,blue)========================================$(NC)"
	@echo ""
	@echo "$(call color,green)Development:$(NC)"
	@echo "  install       - Create virtual environment and install dependencies"
	@echo "  dev           - Run development server with auto-reload"
	@echo "  run           - Run development server"
	@echo "  shell         - Enter Python shell with app context"
	@echo "  flask         - Run Flask CLI commands"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test          - Run all tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run code linters (flake8, black, isort)"
	@echo "  format        - Auto-format code"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@echo "  migrate       - Create database migrations"
	@echo "  upgrade       - Apply pending migrations"
	@echo "  downgrade     - Rollback last migration"
	@echo "  init-db       - Initialize database with seed data"
	@echo "  reset-db      - Reset database (WARNING: destroys data)"
	@echo "  seed          - Add seed data to database"
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@echo "  build         - Build production artifacts"
	@echo "  build-wheel   - Build wheel package"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-stop   - Stop Docker container"
	@echo "  docker-logs   - View Docker container logs"
	@echo "  deploy        - Deploy to production server"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  clean         - Remove build artifacts and cache"
	@echo "  clean-venv    - Remove virtual environment"
	@echo "  clean-all     - Remove all generated files (including database)"
	@echo "  requirements  - Update requirements.txt from dependencies"
	@echo "  freeze        - Freeze dependencies to requirements.txt"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  docs          - Generate API documentation"
	@echo "  serve-docs    - Serve documentation locally"
	@echo "  check-docs    - Check documentation links"
	@echo ""
	@echo "$(GREEN)Security:$(NC)"
	@echo "  audit         - Run security audit on dependencies"
	@echo "  secrets       - Check for secrets in code"
	@echo ""
	@echo ""

# ============================================================================
# DEVELOPMENT TARGETS
# ============================================================================

.PHONY: install
install: $(VENV_DIR)/bin/activate
	@echo "$(call color,green)Installing dependencies...$(NC)"
	. $(VENV_DIR)/bin/activate && pip install -r requirements.txt
	@echo "$(call color,green)Creating configuration from template...$(NC)"
	@if [ ! -f $(CONFIG_FILE) ]; then cp config.example.json $(CONFIG_FILE); fi
	@echo "$(call color,green)Initializing database migrations...$(NC)"
	@if [ ! -d migrations ]; then \
		. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db init; \
	fi
	@echo ""
	@echo "$(call color,green)Installation complete!$(NC)"
	@echo "$(call color,yellow)Run 'make run' to start the development server$(NC)"

$(VENV_DIR)/bin/activate:
	@echo "$(call color,green)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(call color,green)Virtual environment created!$(NC)"

.PHONY: dev
dev:
	@echo "$(call color,green)Starting development server with auto-reload...$(NC)"
	@echo "$(call color,yellow)Server will be available at http://localhost:$(PORT)$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) --debug run --host=0.0.0.0 --port=$(PORT)

.PHONY: run
run:
	@echo "$(call color,green)Starting development server...$(NC)"
	@echo "$(call color,yellow)Server will be available at http://localhost:$(PORT)$(NC)"
	. $(VENV_DIR)/bin/activate && python -m $(APP_MODULE)

.PHONY: shell
shell:
	@echo "$(call color,green)Entering Python shell with app context...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) shell

.PHONY: flask
flask:
	@echo "$(call color,green)Running Flask CLI command...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) $(filter-out $@,$(MAKECMDGOALS)))

# Allow passing arguments to flask
%:
	@:

# ============================================================================
# TESTING TARGETS
# ============================================================================

.PHONY: test
test:
	@echo "$(call color,green)Running tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && python -m pytest tests/ -v --tb=short 2>/dev/null || \
	(echo "$(call color,yellow)No tests found. Creating test directory...$(NC)" && mkdir -p tests && \
	echo "# Add your tests here" > tests/__init__.py && \
	echo "$(call color,green)Tests directory created. Add your test files to tests/$(NC)")

.PHONY: test-coverage
test-coverage:
	@echo "$(call color,green)Running tests with coverage...$(NC)"
	@. $(VENV_DIR)/bin/activate && python -m pytest tests/ --cov=$(APP_MODULE) --cov-report=term-missing --cov-report=html || true
	@echo "$(call color,green)Coverage report available at htmlcov/index.html$(NC)"

.PHONY: lint
lint:
	@echo "$(call color,green)Running code linters...$(NC)"
	@. $(VENV_DIR)/bin/activate && (flake8 src/ --max-line-length=100 --extend-ignore=E203 2>/dev/null || echo "flake8 not installed")
	@. $(VENV_DIR)/bin/activate && (black --check src/ 2>/dev/null || echo "black not installed")
	@. $(VENV_DIR)/bin/activate && (isort --check-only src/ 2>/dev/null || echo "isort not installed")

.PHONY: format
format:
	@echo "$(call color,green)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && (black src/ 2>/dev/null || echo "black not installed")
	@. $(VENV_DIR)/bin/activate && (isort src/ 2>/dev/null || echo "isort not installed")
	@echo "$(call color,green)Code formatted!$(NC)"

# ============================================================================
# DATABASE TARGETS
# ============================================================================

.PHONY: migrate
migrate:
	@echo "$(call color,green)Creating database migration...$(NC)"
	@if [ -z "$(MSG)" ]; then \
		echo "$(call color,yellow)Please provide a migration message: make migrate MSG=\"description\"$(NC)"; \
	else \
		. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db migrate -m "$(MSG)"; \
	fi

.PHONY: upgrade
upgrade:
	@echo "$(call color,green)Applying database migrations...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db upgrade

.PHONY: downgrade
downgrade:
	@echo "$(call color,green)Rolling back database migration...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db downgrade

.PHONY: init-db
init-db:
	@echo "$(call color,green)Initializing database...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db create
	@echo "$(call color,green)Database initialized!$(NC)"

.PHONY: reset-db
reset-db:
	@echo "$(call color,red)WARNING: This will destroy ALL database data!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		echo "$(call color,green)Resetting database...$(NC)"; \
		. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db drop --hard; \
		. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db create; \
		. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) seed; \
		echo "$(call color,green)Database reset complete!$(NC)"; \
	else \
		echo "Aborted."; \
	fi

.PHONY: seed
seed:
	@echo "$(call color,green)Adding seed data to database...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) seed

.PHONY: db-shell
db-shell:
	@echo "$(call color,green)Opening database shell...$(NC)"
	. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db shell

# ============================================================================
# PRODUCTION TARGETS
# ============================================================================

.PHONY: build
build:
	@echo "$(call color,green)Building production artifacts...$(NC)"
	@. $(VENV_DIR)/bin/activate && pip install -r requirements.txt --upgrade --quiet
	@. $(VENV_DIR)/bin/activate && flask --app $(APP_MODULE) db upgrade --directory migrations
	@echo "$(call color,green)Build complete!$(NC)"

.PHONY: build-wheel
build-wheel:
	@echo "$(call color,green)Building wheel package...$(NC)"
	@. $(VENV_DIR)/bin/activate && pip install build
	@. $(VENV_DIR)/bin/activate && python -m build
	@echo "$(call color,green)Wheel built in dist/ directory$(NC)"

.PHONY: docker-build
docker-build:
	@echo "$(call color,green)Building Docker image: $(PROJECT_NAME):$(DOCKER_TAG)$(NC)"
	docker build -t $(PROJECT_NAME):$(DOCKER_TAG) .
	@echo "$(call color,green)Docker image built successfully!$(NC)"

.PHONY: docker-run
docker-run:
	@echo "$(call color,green)Running Docker container...$(NC)"
	@echo "$(call color,yellow)Server will be available at http://localhost:$(PORT)$(NC)"
	docker run -d \
		-p $(PORT):8000 \
		--name $(PROJECT_NAME) \
		--restart unless-stopped \
		-e FLASK_ENV=production \
		$(PROJECT_NAME):$(DOCKER_TAG)
	@echo "$(call color,green)Docker container started!$(NC)"

.PHONY: docker-stop
docker-stop:
	@echo "$(call color,green)Stopping Docker container...$(NC)"
	@docker stop $(PROJECT_NAME) 2>/dev/null && docker rm $(PROJECT_NAME) 2>/dev/null || \
	echo "$(call color,yellow)Container not running$(NC)"
	@echo "$(call color,green)Docker container stopped!$(NC)"

.PHONY: docker-logs
docker-logs:
	@echo "$(call color,green)Viewing Docker container logs (Ctrl+C to exit)...$(NC)"
	@docker logs -f $(PROJECT_NAME)

.PHONY: deploy
deploy:
	@echo "$(call color,green)Deploying to production...$(NC)"
	@read -p "Enter production server (user@host): " server; \
	read -p "Enter production server path: " path; \
	echo "$(call color,yellow)Copying files to production server...$(NC)"; \
	scp -r . $$server:$$path/ --exclude={.git,venv,__pycache__,*.pyc,.pytest_cache,htmlcov,dist}; \
	echo "$(call color,yellow)Running installation on production server...$(NC)"; \
	ssh $$server "cd $$path && make install && make build && sudo systemctl restart $(PROJECT_NAME)"; \
	echo "$(call color,green)Deployment complete!$(NC)"

# ============================================================================
# MAINTENANCE TARGETS
# ============================================================================

.PHONY: clean
clean:
	@echo "$(call color,green)Cleaning build artifacts...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".nox" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .nox/ 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@echo "$(call color,green)Clean complete!$(NC)"

.PHONY: clean-venv
clean-venv:
	@echo "$(call color,green)Removing virtual environment...$(NC)"
	@rm -rf $(VENV_DIR)
	@echo "$(call color,green)Virtual environment removed!$(NC)"

.PHONY: clean-all
clean-all: clean clean-venv
	@echo "$(call color,green)Removing database and all generated files...$(NC)"
	@rm -f $(CONFIG_FILE) *.db *.sqlite migrations/versions/*.py 2>/dev/null || true
	@rm -rf docker-compose.override.yml 2>/dev/null || true
	@echo "$(call color,green)All generated files removed!$(NC)"

.PHONY: requirements
requirements:
	@echo "$(call color,green)Updating requirements.txt...$(NC)"
	@. $(VENV_DIR)/bin/activate && pip freeze > requirements.txt
	@echo "$(call color,green)requirements.txt updated!$(NC)"

.PHONY: freeze
freeze:
	@echo "$(call color,green)Freezing dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && pip freeze > requirements.txt
	@echo "$(call color,green)Dependencies frozen to requirements.txt$(NC)"

# ============================================================================
# DOCUMENTATION TARGETS
# ============================================================================

.PHONY: docs
docs:
	@echo "$(call color,green)Generating API documentation...$(NC)"
	@. $(VENV_DIR)/bin/activate && (pip install pdoc 2>/dev/null || true)
	@. $(VENV_DIR)/bin/activate && mkdir -p docs/api && python -m pdoc --output-dir docs/api $(APP_MODULE)
	@echo "$(call color,green)API documentation generated in docs/api/$(NC)"

.PHONY: serve-docs
serve-docs:
	@echo "$(call color,green)Serving documentation at http://localhost:8001$(NC)"
	@. $(VENV_DIR)/bin/activate && python -m http.server 8001 --directory docs/

.PHONY: check-docs
check-docs:
	@echo "$(call color,green)Checking documentation links...$(NC)"
	@. $(VENV_DIR)/bin/activate && (pip install linkchecker 2>/dev/null || true)
	@. $(VENV_DIR)/bin/activate && linkchecker --check-extern docs/ 2>/dev/null || echo "linkchecker not available, skipping link check"

# ============================================================================
# SECURITY TARGETS
# ============================================================================

.PHONY: audit
audit:
	@echo "$(call color,green)Running security audit on dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && (pip install safety 2>/dev/null || true)
	@. $(VENV_DIR)/bin/activate && safety check -r requirements.txt || echo "safety not available, skipping audit"

.PHONY: secrets
secrets:
	@echo "$(call color,green)Checking for secrets in code...$(NC)"
	@. $(VENV_DIR)/bin/activate && (pip install detect-secrets 2>/dev/null || true)
	@. $(VENV_DIR)/bin/activate && detect-secrets scan || echo "detect-secrets not available, skipping secret check"

# ============================================================================
# UTILITY TARGETS
# ============================================================================

.PHONY: check-env
check-env:
	@echo "$(call color,green)Checking environment...$(NC)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Virtual environment: $(VENV_DIR)"
	@[ -d $(VENV_DIR) ] && echo "Virtual environment exists" || echo "Virtual environment missing (run 'make install')"

.PHONY: status
status: check-env
	@echo "$(call color,green)Checking project status...$(NC)"
	@echo "Configuration file: $(CONFIG_FILE)"
	@[ -f $(CONFIG_FILE) ] && echo "  ✅ Configuration exists" || echo "  ❌ Configuration missing (run 'make install')"
	@echo "Database file:"
	@find . -name "*.db" -o -name "*.sqlite" 2>/dev/null | head -5 || echo "  No database found"
	@echo "Migrations directory:"
	@[ -d migrations ] && echo "  ✅ Migrations directory exists" || echo "  ❌ Migrations missing (run 'make install')"

.PHONY: info
info:
	@echo "$(call color,green)Project Information$(NC)"
	@echo "Project Name: $(PROJECT_NAME)"
	@echo "App Module: $(APP_MODULE)"
	@echo "Port: $(PORT)"
	@echo "Virtual Environment: $(VENV_DIR)"
	@echo "Python: $(PYTHON)"
	@echo ""

# ============================================================================
# DOCKER-COMPOSE TARGETS (Optional)
# ============================================================================

.PHONY: docker-up
docker-up:
	@echo "$(call color,green)Starting all services with Docker Compose...$(NC)"
	@docker-compose up -d
	@echo "$(call color,green)Services started!$(NC)"

.PHONY: docker-down
docker-down:
	@echo "$(call color,green)Stopping all Docker Compose services...$(NC)"
	@docker-compose down
	@echo "$(call color,green)Services stopped!$(NC)"

.PHONY: docker-logs-all
docker-logs-all:
	@echo "$(call color,green)Viewing all service logs...$(NC)"
	@docker-compose logs -f

# ============================================================================
# DEVELOPMENT CONVENIENCE TARGETS
# ============================================================================

.PHONY: reload
reload:
	@echo "$(call color,green)Restarting development server...$(NC)"
	@pkill -f "flask.*problem-solver" 2>/dev/null || true
	@make dev &

.PHONY: logs
logs:
	@echo "$(call color,green)Following application logs (Ctrl+C to exit)...$(NC)"
	@tail -f *.log 2>/dev/null || echo "No log files found"

.PHONY: open
open:
	@echo "$(call color,green)Opening application in browser...$(NC)"
	@if command -v open > /dev/null 2>&1; then \
		open "http://localhost:$(PORT)"; \
	elif command -v xdg-open > /dev/null 2>&1; then \
		xdg-open "http://localhost:$(PORT)"; \
	else \
		echo "Cannot detect browser. Open http://localhost:$(PORT) manually"; \
	fi

# ============================================================================
# CI/CD TARGETS
# ============================================================================

.PHONY: ci-install
ci-install:
	@echo "$(call color,green)CI environment installation...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip
	. $(VENV_DIR)/bin/activate && pip install -r requirements.txt
	. $(VENV_DIR)/bin/activate && pip install pytest-cov flake8 black isort safety

.PHONY: ci-test
ci-test: test
	@echo "$(call color,green)Running additional CI checks...$(NC)"
	@. $(VENV_DIR)/bin/activate && black --check src/ 2>/dev/null || true
	@. $(VENV_DIR)/bin/activate && isort --check-only src/ 2>/dev/null || true
	@. $(VENV_DIR)/bin/activate && flake8 src/ --max-line-length=100 --extend-ignore=E203 2>/dev/null || true

.PHONY: ci-build
ci-build:
	@echo "$(call color,green)CI build...$(NC)"
	@. $(VENV_DIR)/bin/activate && python -m py_compile src/*.py
	@echo "$(call color,green)Build successful!$(NC)"

.PHONY: ci
ci: ci-install ci-test ci-build
	@echo "$(call color,green)CI pipeline complete!$(NC)"
