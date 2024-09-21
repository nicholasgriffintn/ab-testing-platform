# A/B Testing Platform

## Overview
This A/B Testing Platform provides a robust and scalable framework for running A/B tests using both Bayesian and frequentist methods. It supports various statistical methods, bucketing strategies, and multiple testing corrections, making it suitable for a wide range of experimentation needs.

> NOTE: This is just me messing around, don't take it too seriously.

## Features
- **Bayesian and Frequentist A/B Testing**: Supports both Bayesian and Frequentist approaches to A/B testing, providing flexibility depending on your analysis requirements.
- **Bucketing**: Provides functionality for bucketing users into test groups using various strategies.
- **Multiple Testing Corrections**: Includes multiple testing correction algorithms such as Bonferroni, Benjamini-Hochberg, and Holm corrections.
- **Plotting**: Offers built-in plotting tools for visualizing A/B test results.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
   - [CLI](#cli)
3. [Testing](#testing)
4. [Contributing](#contributing)
5. [License](#license)


## Installation

To install and use this platform, you will need [Poetry](https://python-poetry.org/) for dependency management.

1. Clone the repository:
   ```bash
   git clone https://github.com/nicholasgriffintn/ab-testing-platform
   cd ab-testing-platform
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Run tests to ensure everything is working:
   ```bash
   poetry run tox
   ```


## Usage

### CLI

The platform includes a CLI for running A/B tests and interacting with the platform. You can run the CLI using the following command:

```bash
poetry run ab-testing-platform --help
```

This will display the available commands and options for the CLI. For example, you can run a test using the following command:

```bash
poetry run ab-testing-platform ab-testing load-data-from-file
```


## Testing
To run the tests, use `tox`:

```bash
poetry run tox
```


## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any features or improvements. Make sure to add unit tests for any new functionality and update the documentation accordingly.


## License
This project is licensed under the [MIT License](LICENSE).
