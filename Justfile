# ------------------------------------------------------------------------------
# Prettier
# ------------------------------------------------------------------------------

# Check all files with prettier
prettier-check:
    prettier . --check

# Format all files with prettier
prettier-format:
    prettier . --check --write

# ------------------------------------------------------------------------------
# Justfile
# ------------------------------------------------------------------------------

# Format Justfile
format:
    just --fmt --unstable

# Check Justfile formatting
format-check:
    just --fmt --check --unstable

# ------------------------------------------------------------------------------
# Gitleaks
# ------------------------------------------------------------------------------

# Run gitleaks detection
gitleaks-detect:
    gitleaks detect --source .

# ------------------------------------------------------------------------------
# Prek
# ------------------------------------------------------------------------------

# Run prek checking on all pre-commit config files
prek-check:
    find . -name "pre-commit-config.*" -exec prek validate-config -c {} \;

# ------------------------------------------------------------------------------
# Zizmor
# ------------------------------------------------------------------------------

# Run zizmor checking
zizmor-check:
    uvx zizmor . --persona=auditor

# ------------------------------------------------------------------------------
# Actionlint
# ------------------------------------------------------------------------------

# Run actionlint checks
actionlint-check:
    actionlint

# ------------------------------------------------------------------------------
# Pinact
# ------------------------------------------------------------------------------

# Run pinact
pinact-run:
    pinact run

# Run pinact checking
pinact-check:
    pinact run --verify --check

# Run pinact update
pinact-update:
    pinact run --update

# ------------------------------------------------------------------------------
# EditorConfig
# ------------------------------------------------------------------------------

# Check files format with EditorConfig
editorconfig-check:
    editorconfig-checker

# ------------------------------------------------------------------------------
# Git Hooks
# ------------------------------------------------------------------------------

# Install git hooks using prek
install-git-hooks:
    prek install

# ------------------------------------------------------------------------------
# Prek
# ------------------------------------------------------------------------------

# Update prek hooks and additional dependencies
prek-update:
    just prek-update-hooks
    just prek-update-additional-dependencies

# Prek update hooks
prek-update-hooks:
    prek autoupdate

prek-update-additional-dependencies:
    uv run --script https://raw.githubusercontent.com/JackPlowman/update-prek-additional-dependencies/refs/heads/main/update_prek_additional_dependencies.py

# ------------------------------------------------------------------------------
# Update All Tools
# ------------------------------------------------------------------------------

# Update all tools
update:
    just pinact-update
    just prek-update
    just prek-update-additional-dependencies

# ------------------------------------------------------------------------------
# General Commands
# ------------------------------------------------------------------------------

# Install All Python Dependencies
install:
    uv sync --all-extras

# Remove all compiled Python files
clean:
    find . \( \
      -name '__pycache__' -o \
      -name '.coverage' -o \
      -name '.mypy_cache' -o \
      -name '.pytest_cache' -o \
      -name '.ruff_cache' -o \
      -name '*.pyc' -o \
      -name '*.pyd' -o \
      -name '*.pyo' -o \
      -name 'coverage.xml' -o \
      -name 'db.sqlite3' \
    \) -print | xargs rm -rfv

# ------------------------------------------------------------------------------
# Ruff - Python Linting and Formatting
# ------------------------------------------------------------------------------

# Fix all Ruff issues
ruff-fix:
    just ruff-format-fix
    just ruff-lint-fix

# Check for all Ruff issues
ruff-checks:
    just ruff-format-check
    just ruff-lint-check

# Check for Ruff issues
ruff-lint-check:
    uv run ruff check update_prek_additional_dependencies.py

# Fix Ruff lint issues
ruff-lint-fix:
    uv run ruff check update_prek_additional_dependencies.py --fix --unsafe-fixes

# Check for Ruff format issues
ruff-format-check:
    uv run ruff format --check update_prek_additional_dependencies.py

# Fix Ruff format issues
ruff-format-fix:
    uv run ruff format update_prek_additional_dependencies.py

# ------------------------------------------------------------------------------
# Ty - Python Type Checking
# ------------------------------------------------------------------------------

# Check for type issues with Ty
ty-check:
    uv run ty check update_prek_additional_dependencies.py

# ------------------------------------------------------------------------------
# Other Python Tools
# ------------------------------------------------------------------------------

# Check uv lockfile
uv-lock-check:
    uv lock --check
