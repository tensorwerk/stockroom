#!/usr/bin/env bash

set -e
set -x

mypy stockroom
black stockroom tests --check
isort stockroom tests --check-only

export PYTHONPATH=./docs_src
pytest --cov=stockroom --cov=tests --cov-report=term-missing --cov-report=xml tests ${@}
