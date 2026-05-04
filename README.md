# gherkin-lint

Linter for Gherkin feature files with a Python module and CLI interface.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

Install the project and development dependencies with uv:

```bash
uv sync --all-groups
```

Run the CLI from the local checkout:

```bash
uv run gherkin-lint --help
```

Alternatively, run the module directly:

```bash
uv run python -m gherkin_lint --help
```

## Usage

Lint one feature file:

```bash
uv run gherkin-lint features/login.feature
```

Lint multiple feature files:

```bash
uv run gherkin-lint features/login.feature features/checkout.feature
```

Lint all feature files in a directory using shell globbing:

```bash
uv run gherkin-lint features/*.feature
```

Use a different indentation width for scenarios inside rules:

```bash
uv run gherkin-lint --indent-size 2 features/*.feature
```

Increase verbosity:

```bash
uv run gherkin-lint -v features/login.feature
uv run gherkin-lint -vv features/login.feature
```

Write output to a log file:

```bash
uv run gherkin-lint --logfile gherkin-lint.log features/*.feature
```

The command exits with status code `0` if no linting errors are found and with status code `1` if at least one linting error is found.

## Tests

Run the pytest test suite:

```bash
uv run --group test pytest
```

Run a single test module:

```bash
uv run --group test pytest tests/test_doc_feature_ok.py
```

Run tests through tox:

```bash
uvx --with tox-uv tox
```

Run a specific tox environment:

```bash
uvx --with tox-uv tox -e py312
uvx --with tox-uv tox -e py313
uvx --with tox-uv tox -e lint
```

## Linting and formatting

Run Ruff checks:

```bash
uv run --group lint ruff check .
```

Check formatting:

```bash
uv run --group lint ruff format --check .
```

Apply formatting:

```bash
uv run --group lint ruff format .
```

## Build

Build source distribution and wheel:

```bash
uv build
```

The generated artifacts are written to `dist/`.

## Development workflow

A typical local workflow is:

```bash
uv sync --all-groups
uv run --group lint ruff check .
uv run --group lint ruff format --check .
uv run --group test pytest
uv build
```
