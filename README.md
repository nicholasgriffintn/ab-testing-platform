# AB Testing Platform

This is a simple AB Testing Platform that allows you to perform AB Testing on a set of users.

With the CLI you can load users from a file, or enter them manually.

> NOTE: This is just me messing around, don't take it too seriously.

## Getting Started

First you will need to install [Poetry](https://python-poetry.org/docs/) and install the dependencies, you can do this with:

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="${HOME}/.local/bin:${PATH}" && \
poetry env use 3.13 && \
poetry install
```

Then you can run the platform with:

```bash
poetry run python -m ab_testing_platform --help
```

This will output the available commands and options.

For example to run from a file, you can do:

```bash
poetry run python -m ab_testing_platform ab-testing load-data-from-file --file_path=./tests/fixtures/ab-testing-users.json
```

## Running the tests

You can run the tests with:

```bash
poetry run python -m tox
```