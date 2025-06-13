#!/usr/bin/env bash
# This script is used to run tests and generate coverage reports.

set -e # Exit immediately if a command exits with a non-zero status
set -x # Print each command before executing it

# Run tests with coverage
coverage run --source=app -m pytest -s

# Generate coverage reports
coverage report --show-missing

# Generate HTML coverage reportren
coverage html --title "${@-coverage}" 